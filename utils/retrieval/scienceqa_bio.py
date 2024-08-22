# scienceqa_bio
from typing import Optional, Any
import transformers
import torch
from peft import PeftModel
from transformers.utils import is_accelerate_available, is_bitsandbytes_available
from transformers import (
    AutoModel,
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
    pipeline,
)
import re
import utils.globalvar
import datasets

# prompt = """
# ### Instruction: Answer the question truthfully.
# ### Input: What are some possible causes of low PTH and high calcium levels?
# ### Output: 
# """

def formatting_prompts_func(ipt):
    text = f"### Instruction: Answer the question truthfully.\n### Input: {ipt}\n### Output: "
    return text


### Query Generation ###############################################
def llama2_pipeline(prompt):
    base_model = "meta-llama/Llama-2-7b-hf"
    peft_model = "veggiebird/llama-2-7b-biology-scienceqa-8bit"
    
    # load the model only once
    #加载一次模型和分词器
    if utils.globalvar.bio_model is None:
        utils.globalvar.bio_model = AutoModelForCausalLM.from_pretrained(
            base_model,
            use_safetensors=True,
            torch_dtype=torch.float16,
            load_in_8bit=True
        )
        # 加载微调后的模型
        utils.globalvar.bio_model = PeftModel.from_pretrained(utils.globalvar.bio_model, peft_model)
        # 加载分词器
        utils.globalvar.bio_tokenizer = AutoTokenizer.from_pretrained(base_model)
    
    print("Model loaded...")

    pipeline = transformers.pipeline(
        #任务类型
        "text-generation",
        #模型
        model=utils.globalvar.bio_model,
        #分词器
        tokenizer=utils.globalvar.bio_tokenizer,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    #调用
    sequences = pipeline(
        prompt,
        do_sample=False,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=utils.globalvar.bio_tokenizer.eos_token_id,
        max_length=256,
    )

    #返回结果
    return sequences[0]["generated_text"].strip()

###############################################

### Query Knowl. ###############################################
def extract_responses(content):
    # raw string没有转译的字符串
    pattern = r"### Output:(.+?)###"
    #正则匹配output内容
    matches = re.findall(pattern, content, re.DOTALL)
    #去掉匹配的output的前后空格，并返回
    return [match.strip() for match in matches]


def generate_scienceqa_bio_query(input):
    prompt = formatting_prompts_func(input)
    query = llama2_pipeline(prompt)
    processed_query = extract_responses(query)
    return query, processed_query


def execute_scienceqa_bio_query(query):
    # 加载模型 simCSE对比句向量表征模型
    model = AutoModel.from_pretrained("princeton-nlp/sup-simcse-roberta-large")
    # 加载分词器
    tokenizer = AutoTokenizer.from_pretrained("princeton-nlp/sup-simcse-roberta-large")
    # 加载数据集
    dataset = datasets.load_dataset('veggiebird/biology-scienceqa')
    # 加载训练集
    dataset = dataset["train"]

    # 创建faiss索引
    dataset.add_faiss_index(column='embeddings')

    # 将查询编码
    query_inputs = tokenizer(query, padding=True, truncation=True, return_tensors="pt")

    # 生成句子的特征向量 **是dict参数；pooler_output:Pooler层处理后得到的输出结果，
    query_embedding = model(**query_inputs, output_hidden_states=True, return_dict=True).pooler_output.detach().numpy()

    #获取最近的数据
    scores, retrieved_Examples = dataset.get_nearest_examples("embeddings", query_embedding, k=1)

    #获得过滤后的知识
    pre_knowl = retrieved_Examples["output"][0].strip()
    try:
        knowl = ' '.join(re.split(r'(?<=[.:;])\s', pre_knowl)[:3])
    except:
        knowl = pre_knowl
    return knowl

###############################################

def retrieve_scienceqa_bio_knowledge(input, data_point):
    knowl = ""
    print("Generate query...")
    query, processed_query = generate_scienceqa_bio_query(input)
    if len(processed_query) != 0:
        print("Query:", processed_query[0])
        print("Retrieve knowledge...")
        knowl = execute_scienceqa_bio_query(processed_query[0])
    print(knowl)
    return knowl