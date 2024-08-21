# 设置

## 1. 使用 conda虚拟环境

```bash
conda activate ka-llm
```

## 2. 配置代理

```bash
#进入目录
cd clash-for-linux
#运行启动脚本
sudo bash start.sh
#加载环境变量
source /etc/profile.d/clash.sh
#启动服务
proxy_on
#检查端口
netstat -tln | grep -E '9090|789.'
```

### 使用dashBoard 配置代理
>在vscode中配置转发端口，9090，转发地址为**localhost:9090**

同时，需要知道配置文件的secret，可以在`conf/config.yaml`中的secret中找到，
在**localhost:9090/ui**中配置好url和secret就可以配置代理了，需要使用美国节点。

## 2. 配置 OPENAI_API_KEY和SERPAPI_KEY

```bash
#进入项目目录
cd ~/CHI-2025-Human-AI/internal/chain-of-knowledge
#配置环境变量
export OPENAI_API_KEY=your key
export SERPAPI_KEY=your key
```

## 4. llama2 token 登录

```bash
huggingface-cli login
```

## 5. 启动项目 
```bash
python run.py --model gpt-3.5-turbo-0613 --dataset hotpotqa --output outputs/hotpotqa/hotpotqa_output.json --step True
```

# QA的格式

```python
data_point={
    #初始的内容
    "question": '' , #问题
    "answer": '' , #数据集的答案
    "id": 0, #编号

    #阶段1，推理准备阶段
    "s1_domains": [], #问题的领域
    "cot_response": '', #第一个的完整回答
    "cot_answer": '', #第一个回答中的答案
    "cot_sc_score": '', #分数，五个回答中次数最多的答案的占比
    "cot_sc_response": '', #次数最多的那次回答的完整回答
    "cot_sc_answer": '', #次数最多的那次回答中的答案
    "cot_sc_rationales": ['rationale_1','rationale_2'], #次数最多的那次回答中的理由1，理由2

    #阶段2 知识适应阶段
    "rationale_1_knowl": {}, #理由1的知识字典
    "edited_rationale_1": '', #知识适应之后的新的理由1
    "new_rationale_2": '', #根据新的理由1产生的初始理由2
    "rationale_2_knowl": {}, #理由2的知识字典
    "edited_rationale_2": '', #知识适应之后的新的理由2

    #阶段3 答案整合阶段
    "final_answer": '', #根据知识适应后的新的理由1和理由2生成的最终答案
}
```

# Chain-of-Knowledge

### 1. Requirements
#### 1.1 OPENAI_API_KEY
Create an account and get the API key for OpenAI (https://openai.com).

```
OPENAI_API_KEY=YOUR_KEY
```
#### 1.2 SERPAPI_KEY
Create an account and get the API key for google retrieval (https://serpapi.com).

```
SERPAPI_KEY=YOUR_KEY
```

#### 1.3 Install requirements
```
conda env create -f requirements.yaml
```

#### 1.4 Setup Entity Linking for SPARQL

For linking text to KG facts using pretrained models for now.

Download mGENRE entity linking files:

```
mkdir -p utils/retrieval/linking_data/genre
cd utils/retrieval/linking_data/genre
wget https://dl.fbaipublicfiles.com/GENRE/lang_title2wikidataID-normalized_with_redirect.pkl
wget https://dl.fbaipublicfiles.com/GENRE/titles_lang_all105_marisa_trie_with_redirect.pkl
cd ../..
```

Preprocess entity information:

```
python linking.py process_titles
```

### 2. Instruction-tuning of adaptive query generator (AQG)
```
python sft_trainer.py \
    --model_name $BASE_MODEL \
    --dataset_name $DATASET_NAME \
    --load_in_8bit \
    --use_peft \
    --batch_size 32 \
    --gradient_accumulation_steps 2 \
    --output_dir $OUTPUT_DIR \
    --num_train_epochs 3 \
    --push_to_hub True\
    --hub_model_id $HUB_MODEL_ID \
```

### 3. Inference chain-of-knowledge (CoK)
```
python run.py \
    --model gpt-3.5-turbo-0613 \
    --dataset $DATASET_NAME \
    --output $OUTPUT_DIR \
    --step True \
```

### Citation
```
@inproceedings{
    li2024cok,
    title={Chain-of-Knowledge: Grounding Large Language Models via Dynamic Knowledge Adapting over Heterogeneous Sources},
    author={Xingxuan Li and Ruochen Zhao and Yew Ken Chia and Bosheng Ding and Shafiq Joty and Soujanya Poria and Lidong Bing},
    booktitle={International Conference on Learning Representations},
    year={2024},
    url={https://openreview.net/forum?id=cPgh4gWZlz}
}
```
