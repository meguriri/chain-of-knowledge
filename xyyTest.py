'''
{
    "question": "Where were the Olympics held when the 1993 World Champion 
        figure skater's home country won it's second Winter Games gold medal?",
    "answer": "Sochi, Russia", 
    "id": 0, 
    "s1_domains": ["factual"], 
    "cot_response": "First, the 1993 World Champion figure skater 
        is Oksana Baiul from Ukraine. Second, Ukraine won its second 
        Winter Games gold medal at the 1994 Winter Olympics. 
        The answer is Lillehammer, Norway.", 
    "cot_answer": "lillehammer, norway.", 
    "cot_sc_score": 0.8, 
    "cot_sc_response": "First, the 1993 World Champion 
        figure skater is Oksana Baiul from Ukraine. Second, Ukraine 
        won its second Winter Games gold medal at the 1994 Winter Olympics. 
        The answer is Lillehammer, Norway.",
    "cot_sc_answer": "lillehammer, norway.", 
    "cot_sc_rationales": ["the 1993 World Champion figure skater is 
        Oksana Baiul from Ukraine.", "Ukraine won its second Winter 
        Games gold medal at the 1994 Winter Olympics."]
}
'''

'''一个gpt的响应
{
  "id": "chatcmpl-12345",  # 唯一标识符
  "object": "chat.completion",  # 返回对象的类型
  "created": 1689374873,  # 创建的时间戳
  "model": "gpt-4",  # 使用的模型名称
  "choices": [
    {
      "index": 0,  # 响应的索引（从0开始）
      "message": {
        "role": "assistant",
        "content": "Why don't scientists trust atoms? Because they make up everything!"  # 模型生成的文本
      },
      "finish_reason": "stop"  # 停止生成的原因，如“stop”表示完成，“length”表示达到max_tokens限制
    }
  ],
  "usage": {
    "prompt_tokens": 20,  # 提示消息（输入）的token数
    "completion_tokens": 15,  # 生成文本（输出）的token数
    "total_tokens": 35  # 总的token数
  }
}
1.	id: 每个响应都有一个唯一的ID，用于标识该生成请求。
	2.	object: 表明返回的对象类型，这里是 "chat.completion"。
	3.	created: 返回生成响应的时间戳。
	4.	model: 指示使用的模型名称，例如 "gpt-4"。
	5.	choices: 这是一个列表，包含生成的一个或多个响应（取决于你请求生成多少个 n）。
	•	index: 这是生成响应的索引（从0开始计数）。
	•	message: 这是实际的助手响应部分，包括 role 和 content。
	•	role: 这里是 "assistant"，表示这是助手的回复。
	•	content: 模型生成的文本内容。
	•	finish_reason: 表示生成停止的原因。可能值包括 "stop"（自然结束），"length"（达到最大令牌数），"content_filter"（内容被过滤器拦截）等。
	6.	usage: 表示本次API调用的token使用情况：
	•	prompt_tokens: 用户提供的消息的token数量。
	•	completion_tokens: 模型生成的响应的token数量。
	•	total_tokens: 两者之和，指示整个请求中使用的总token数量。
'''
import json #json解析

#openAI utils
from utils.openai_utils import call_openai_api

#不同数据集的提示 utilss
from utils.other_prompts import domain_selection_demonstration

from utils.hotpotqa_parser import hotpotqa

#数据集为hotpotqa
dataset = hotpotqa()

data = dataset.get_dataset()

def retrieve_wikidata_knowledge(s):
   return s

def retrieve_wikipedia_knowledge(s):
   return s

def retrieve_uptodate_knowledge(s):
  return s

def retrieve_scienceqa_bio_knowledge(s):
   return s

def retrieve_ck12_knowledge(s):
   return s

def retrieve_scienceqa_phy_knowledge(s):
   return s


def retrieve_physicsclassroom_knowledge(s):
   return s

domain_mapping = {
    "factual": {
        "wikidata": retrieve_wikidata_knowledge,
        # "wikitable": retrieve_wikitable_knowledge,
        # "dpr": retrieve_dpr_knowledge,
        "wikipedia": retrieve_wikipedia_knowledge,
    },
    "medical": {
        # "flashcard": retrieve_flashcard_knowledge,
        "uptodate": retrieve_uptodate_knowledge,
    },
    "biology": {
        "scienceqa_bio": retrieve_scienceqa_bio_knowledge,
        "ck12": retrieve_ck12_knowledge,
    },
    "physical": {
        "scienceqa_phy": retrieve_scienceqa_phy_knowledge,
        "physicsclassroom": retrieve_physicsclassroom_knowledge,
    },
}


##################### test s1
def test_s1():
    for i in range(1):
        data_point = data[i]
        data_point["id"] = i
        question = dataset.get_question(data_point)

        domin_question = domain_selection_demonstration + "Q: "+ question.strip() + "\nRelevant domains: "

        # domain_response = call_openai_api('gpt-4', 
        #                                   domin_question, 
        #                                   max_tokens=256, 
        #                                   temperature=0
        #                                   )
        # if domain_response is not None:
        #     # gpt回复的内容content（可能是多个域domain）
        #     domain_selection_text_response = domain_response[1].strip()
        #     print("****** Relevant domains:", domain_selection_text_response)
        #     # 将多个域转换成列表保存到data_point的s1_domain中
        #     data_point["s1_domains"] = [x.strip() for x in domain_selection_text_response.split(",")]

        #带提示格式的问题
        # cot_prompt = dataset.get_s1_prompt(question)
        # cot_sc_responses = call_openai_api('gpt-4', cot_prompt, max_tokens=256, temperature=0.7, n=10)

        # if cot_sc_responses is not None:
        #     # 获取全部的回答content
        #     all_cot_text_response = [x["message"]["content"].strip() for x in cot_sc_responses[0]["choices"]] # for chat models
        #     print(all_cot_text_response)
        #     print('-------------------')
        all_cot_text_response=['First, the 1993 World Champion figure skater is Oksana Baiul from Ukraine. Second, Ukraine won its second Winter Games gold medal in the 1994 Winter Olympics. The 1994 Winter Olympics were held in Lillehammer, Norway. The answer is Lillehammer, Norway.', 'First, the 1993 World Champion figure skater is Oksana Baiul who is from Ukraine. Second, Ukraine won its second Winter Games gold medal at the 1994 Olympics. The answer is Lillehammer, Norway.', 'First, the 1993 World Champion figure skater was Oksana Baiul from Ukraine. Second, Ukraine won its second Winter Games gold medal in the 1994 Winter Olympics. The 1994 Winter Olympics were held in Lillehammer, Norway. The answer is Lillehammer, Norway.', 'First, the 1993 World Champion figure skater is from the United States. Second, the United States won its second Winter Games gold medal in the 1960 Olympics. The answer is Squaw Valley, USA.', 'First, the 1993 World Champion figure skater is Oksana Baiul who is from Ukraine. Second, Ukraine won its second Winter Games gold medal at the 1994 Lillehammer Olympics. The answer is Lillehammer.', 'First, the 1993 World Champion figure skater is Oksana Baiul from Ukraine. Second, Ukraine won its second Winter Olympics gold medal in 1994. The 1994 Winter Olympics were held in Lillehammer, Norway. The answer is Lillehammer, Norway.', 'First, the 1993 World Champion figure skater is Oksana Baiul from Ukraine. Second, Ukraine won its second Winter Games gold medal at the 1994 Winter Olympics. The 1994 Winter Olympics were held in Lillehammer, Norway. The answer is Lillehammer, Norway.', 'First, the 1993 World Champion figure skater is Oksana Baiul from Ukraine. Second, Ukraine won its second Winter Games gold medal at the 1994 Lillehammer Olympics. The answer is Lillehammer.', 'First, the 1993 World Champion figure skater is Oksana Baiul from Ukraine. Second, Ukraine won its second Winter Games gold medal at the 1994 Olympics. The answer is Lillehammer, Norway.', 'First, the 1993 World Champion figure skater is Oksana Baiul from Ukraine. Second, Ukraine won its second Winter Games gold medal in 1994. The 1994 Winter Olympics were held in Lillehammer, Norway. The answer is Lillehammer, Norway.']
        
        all_cot_results = []
            
        #遍历10个回答
        for x in all_cot_text_response:
          if "The answer is" in x:
            all_cot_results.append(x.split("The answer is")[1].strip().lower())
          else:
            None
        
        most_common_answer = max(set(all_cot_results), key = all_cot_results.count)
        most_common_answer_indices = [i for i, x in enumerate(all_cot_results) if x == most_common_answer]
        
        sc_score = float(len(most_common_answer_indices)) / len(all_cot_results)

        cot_sc_text_response = all_cot_text_response[most_common_answer_indices[0]]
        cot_sc_rationale_1 = cot_sc_text_response.split("Second, ")[0].strip().split("First, ")[1].strip()
        cot_sc_rationale_2 = cot_sc_text_response.split("Second, ")[1].strip().split("The answer is")[0].strip()
        
        data_point["cot_response"] = all_cot_text_response[0]
        #第一个回答中的答案
        data_point["cot_answer"] = all_cot_results[0]
        #分数，五个回答中次数最多的答案的占比
        data_point["cot_sc_score"] = sc_score
        #次数最多的那次回答的完整内容
        data_point["cot_sc_response"] = cot_sc_text_response
        #次数最多的那次回答中的答案
        data_point["cot_sc_answer"] = most_common_answer
        #次数最多的那次回答中的理由1，理由2
        data_point["cot_sc_rationales"] = [cot_sc_rationale_1, cot_sc_rationale_2]

        # data[i]=data_point
        
        # with open('./test/output1.json', "w") as f:
        #   json.dump(data, f)
        return data_point


##################### test s2
def test_s2(data_point):
  domain =['computer','factual','biology','medical']
  domain = [x if x in domain_mapping else "factual" for x in domain]
  domain = list(dict.fromkeys(domain))

  knowl = {}

  for x in domain:
    knowl[x] = {}
    domain_sources = domain_mapping[x]
    for y in domain_sources:
      tmpl = domain_sources[y](x)
      knowl[x][y] = tmpl

  print(knowl)

if __name__ == '__main__':
   test_s2(1)