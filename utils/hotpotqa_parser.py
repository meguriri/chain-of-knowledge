import os
import json
from utils.openai_utils import call_openai_api
from utils.knowl_query import retrieve_knowledge
from utils.other_prompts import hotpotqa_s1_prompt_demonstration, hotpotqa_s2_edit_prompt_demonstration

class hotpotqa:
    def __init__(self):
        # load data
        with open("datasets/hotpotqa/simplified_data.json", "r") as f:
            self.data = json.load(f)
        
        # s1_prompt
        # s1阶段的提问添加提示格式，cot？
        self.s1_prompt_demonstration = hotpotqa_s1_prompt_demonstration
        
        # s2_edit_prompt
        self.s2_edit_prompt_demonstration = hotpotqa_s2_edit_prompt_demonstration
        
    #获取数据集
    def get_dataset(self):
        return self.data
    #获取问题
    def get_question(self, data_point):
        return data_point["question"]
    
    def get_ground_truth(self, data_point):
        return data_point["answer"]
    
    #获取带有提示格式，符合格式的问题 Q：A： 
    def get_s1_prompt(self, question):
        return self.s1_prompt_demonstration + "Q: " + question.strip() + "\nA: "

    def get_s2_edit_prompt(self, rationale, rationale_knowledge):
        #带理由的提示的初始结构
        sentence = self.s2_edit_prompt_demonstration + "Sentence: " + rationale + "\nKnowledge: "
        #遍历知识字典
        for x in rationale_knowledge:
            #遍历知识来源
            for y in rationale_knowledge[x]:
                sentence += rationale_knowledge[x][y] + " "
        sentence += "\nEdited sentence: "
        return sentence

    def get_s3_consolidation_prompt(self, question, rationale_1, rationale_2):
        return self.s1_prompt_demonstration + "Q: " + question.strip() + "\nA: First, " + rationale_1 + " Second, " + rationale_2 + " The answer is "
    
    #
    def get_cot_sc_results(self, data_point, model, cot_prompt):
        #向gpt发起请求 ，使用带提示的question，得到回答,回答数量为10个，温度0.7，让回答随机一些
        cot_sc_responses = call_openai_api(model, cot_prompt, max_tokens=256, temperature=0.7, n=10)

        #如果回答不为空
        if cot_sc_responses is not None:
            
            # 获取全部的回答content
            all_cot_text_response = [x["message"]["content"].strip() for x in cot_sc_responses[0]["choices"]] # for chat models
            # all_cot_text_response = [x["text"].strip() for x in cot_sc_responses[0]["choices"]] # for text models
            
            #定义result
            all_cot_results = []
            
            #遍历10个回答
            for x in all_cot_text_response:
                #整理回答，得到the answer is后面的内容，并转换为小写，加入到all_cot_results中
                if "The answer is" in x:
                    all_cot_results.append(x.split("The answer is")[1].strip().lower())
                else:
                    None
            
            #选择前五个
            all_cot_results = all_cot_results[:5]
            # all_cot_results = [x.split("The answer is")[1].strip().lower() for x in all_cot_text_response]
            
            # find the most common answer and indices in all_cot_results
            #set(all_cot_results)：去重；key = all_cot_results.count：max的key，按照出现次数最多的选择；max()：选择最大的answer
            most_common_answer = max(set(all_cot_results), key = all_cot_results.count)
            #获取all_cot_results中回答为most_common_answer的索引值
            most_common_answer_indices = [i for i, x in enumerate(all_cot_results) if x == most_common_answer]
            
            #获得分数，算法：all_cot_results中 most_common_answer的比例
            sc_score = float(len(most_common_answer_indices)) / len(all_cot_results)
            
            # use the first answer as cot answer
            #？？？使用all_cot_results中的第一个作为cot_answer
            cot_answer = all_cot_results[0]
            
            # cot_sc answer and rationales
            #保存出现次数最多的那次回答的完整内容
            cot_sc_text_response = all_cot_text_response[most_common_answer_indices[0]]
            #获得first之后，second之前的内容,作为理由1（rationale_1）
            cot_sc_rationale_1 = cot_sc_text_response.split("Second, ")[0].strip().split("First, ")[1].strip()
             #获得second之后，The answer is之前的内容,作为理由2（rationale_2）
            cot_sc_rationale_2 = cot_sc_text_response.split("Second, ")[1].strip().split("The answer is")[0].strip()
            #将出现次数最多的那次回答的答案保存在cot_sc_answer
            cot_sc_answer = most_common_answer
        else:
            #报错
            raise Exception("Stage 1: OpenAI API call failed")
        
        # store the results
        #第一个回答的完整回答
        data_point["cot_response"] = all_cot_text_response[0]
        #第一个回答中的答案
        data_point["cot_answer"] = cot_answer
        #分数，五个回答中次数最多的答案的占比
        data_point["cot_sc_score"] = sc_score
        #次数最多的那次回答的完整内容
        data_point["cot_sc_response"] = cot_sc_text_response
        #次数最多的那次回答中的答案
        data_point["cot_sc_answer"] = cot_sc_answer
        #次数最多的那次回答中的理由1，理由2
        data_point["cot_sc_rationales"] = [cot_sc_rationale_1, cot_sc_rationale_2]

        return data_point
    '''
    通过检索知识，更新理由
    通过更新好的理由1来更新理由2
    '''
    def update_rationales_step_by_step(self, model, data_point):
        #获取该问题的知识域
        domains = data_point["s1_domains"]
        #获取两个理由
        rationales = [x.strip() for x in data_point["cot_sc_rationales"]]
        #理由1
        rationale_1 = rationales[0]
        #理由2
        rationale_2 = rationales[1]

        print("****** Editing Rationale 1 ...")
        # retrieve knowledge for rationale 1 first
        #检索理由1的知识，为一个字典，每个域为key，对应一个检索字典，key为检索网站，value为检索结果
        rationale_1_knowl = retrieve_knowledge(domains, rationale_1, data_point)

        # edit rationale 1 based on rationale 1_knowl
        #获取带知识与理由的提示
        s2_edit_prompt_rationale_1 = self.get_s2_edit_prompt(rationale_1, rationale_1_knowl)
        # print(s2_edit_prompt_rationale_1)

        # 得到知识适应后的理由 edited_rationale_1
        edited_rationale_1 = call_openai_api(model, s2_edit_prompt_rationale_1, max_tokens=256, temperature=0, n=1)[1].strip()
        print("*** Original rationale 1:", rationale_1)
        print("*** Edited rationale 1:", edited_rationale_1)
        
        print("****** Editing Rationale 2 ...")
        # generate rationale 2 using edited rationale 1
        #根据修改后的理由1生成带有新的First的提示
        new_rationale_2_prompt = self.s1_prompt_demonstration + "Q: " + data_point["question"].strip() + "\nA: First, " + edited_rationale_1 + " Second, "
        # print(new_rationale_2_prompt)
        #通过gpt获取回答
        new_rationale_2 = call_openai_api(model, new_rationale_2_prompt, max_tokens=256, temperature=0, n=1)[1].strip()
        # get the rationale, remove the answer sentence
        #获得SECOND后，The answer is 前的内容，也就是理由2
        new_rationale_2 = new_rationale_2.split("The answer is")[0].strip()
        print("*** New rationale 2:", new_rationale_2)

        #理由1的知识字典
        data_point["rationale_1_knowl"] = rationale_1_knowl
        #知识适应之后的新的理由1
        data_point["edited_rationale_1"] = edited_rationale_1
        # 根据新的理由1产生的初始理由2
        data_point["new_rationale_2"] = new_rationale_2

        # retreive knowledge for rationale 2
        # 检索新的理由2的知识，为一个字典，每个域为key，对应一个检索字典，key为检索网站，value为检索结果
        rationale_2_knowl = retrieve_knowledge(domains, new_rationale_2, data_point)

        # edit rationale 2 based on rationale 2_knowl
        #获取带知识与理由的提示
        s2_edit_prompt_rationale_2 = self.get_s2_edit_prompt(new_rationale_2, rationale_2_knowl)
        # print(s2_edit_prompt_rationale_2)
        #得到知识适应后的理由2 edited_rationale_2
        edited_rationale_2 = call_openai_api(model, s2_edit_prompt_rationale_2, max_tokens=256, temperature=0, n=1)[1].strip()
        print("*** Original rationale 2:", rationale_2)
        print("*** Edited rationale 2:", edited_rationale_2)

        # store the results
        # 理由2的知识字典
        data_point["rationale_2_knowl"] = rationale_2_knowl
        # 知识适应之后的新的理由2
        data_point["edited_rationale_2"] = edited_rationale_2

        return data_point

    '''
     通过检索知识，更新理由
     分两次更新理由1和理由2，两次之间没有关联
     '''
    def update_rationales_at_once(self,model,data_point):
        # 获取该问题的知识域
        domains = data_point["s1_domains"]
        # 获取两个理由
        rationales = [x.strip() for x in data_point["cot_sc_rationales"]]
        # 理由1
        rationale_1 = rationales[0]
        # 理由2
        rationale_2 = rationales[1]

        print("****** Editing Rationale 1 ...")
        # retrieve knowledge for rationale 1 first
        rationale_1_knowl = retrieve_knowledge(domains, rationale_1, data_point)

        # edit rationale 1 based on rationale 1_knowl
        s2_edit_prompt_rationale_1 = self.get_s2_edit_prompt(rationale_1, rationale_1_knowl)
        # print(s2_edit_prompt_rationale_1)
        edited_rationale_1 = call_openai_api(model, s2_edit_prompt_rationale_1, max_tokens=256, temperature=0, n=1)[1].strip()
        print("*** Original rationale 1:", rationale_1)
        print("*** Edited rationale 1:", edited_rationale_1)
        
        print("****** Editing Rationale 2 ...")        
        
        data_point["rationale_1_knowl"] = rationale_1_knowl
        data_point["edited_rationale_1"] = edited_rationale_1

        # retreive knowledge for rationale 2
        rationale_2_knowl = retrieve_knowledge(domains, rationale_2, data_point)

        # edit rationale 2 based on rationale 2_knowl
        s2_edit_prompt_rationale_2 = self.get_s2_edit_prompt(rationale_2, rationale_2_knowl)
        # print(s2_edit_prompt_rationale_2)
        edited_rationale_2 = call_openai_api(model, s2_edit_prompt_rationale_2, max_tokens=256, temperature=0, n=1)[1].strip()
        print("*** Original rationale 2:", rationale_2)
        print("*** Edited rationale 2:", edited_rationale_2)

        # store the results
        data_point["rationale_2_knowl"] = rationale_2_knowl
        data_point["edited_rationale_2"] = edited_rationale_2

        return data_point

    
    def get_final_answer(self, model, data_point):
        print("****** Edited rationales: ", "First, " + data_point["edited_rationale_1"] + " Second, " + data_point["edited_rationale_2"])

        #获取最终的问题，携带上原问题和两个经过知识适应的理由，并发送给个gpt
        s3_answer_consolidation_prompt = self.get_s3_consolidation_prompt(data_point["question"], data_point["edited_rationale_1"], data_point["edited_rationale_2"])

        #通过gpt得到最终的回答
        final_answer = call_openai_api(model, s3_answer_consolidation_prompt, max_tokens=256, temperature=0, n=1)[1].strip()

        #保存最终回答
        data_point["final_answer"] = final_answer
        print("****** Final answer:", final_answer)

        #初始的最优答案
        print("****** Original answer:", data_point["cot_sc_answer"])

        #数据集中的正确答案
        print("****** Gold answer:", data_point["answer"])

        #返回最终的QA字典
        return data_point
