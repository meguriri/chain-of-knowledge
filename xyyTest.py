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

for i in range(5):
    data_point = data[i]
    data_point["id"] = i
    question = dataset.get_question(data_point)

    domin_question = domain_selection_demonstration + "Q: "+ question.strip() + "\nRelevant domains: "

    domain_response = call_openai_api('gpt-4', 
                                      domin_question, 
                                      max_tokens=256, 
                                      temperature=0
                                      )
    if domain_response is not None:
        print(domain_response)

