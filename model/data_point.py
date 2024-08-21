'''
    推理预处理阶段的数据格式
'''
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

example_data_point={
       'question': "Where were the Olympics held when the 1993 World Champion figure \
          skater's home country won it's second Winter Games gold medal?", 

        'answer': 'Sochi, Russia', 

        'id': 0, 

        'cot_response': 'First, the 1993 World Champion figure skater is Oksana Baiul from Ukraine. \
          Second, Ukraine won its second Winter Games gold medal in the 1994 Winter Olympics. The 1994\
          Winter Olympics were held in Lillehammer, Norway. The answer is Lillehammer, Norway.', 

        'cot_answer': 'lillehammer, norway.', 
        
        'cot_sc_score': 0.7, 
        
        'cot_sc_response': 'First, the 1993 World Champion figure skater is Oksana Baiul from Ukraine. \
          Second, Ukraine won its second Winter Games gold medal in the 1994 Winter Olympics. The 1994 \
          Winter Olympics were held in Lillehammer, Norway. The answer is Lillehammer, Norway.', 
        
        'cot_sc_answer': 'lillehammer, norway.', 
        
        'cot_sc_rationales': ['the 1993 World Champion figure skater is Oksana Baiul from Ukraine.', 
          'Ukraine won its second Winter Games gold medal in the 1994 Winter Olympics.\
          The 1994 Winter Olympics were held in Lillehammer, Norway.']
  }


'''
知识适应阶段的数据
'''
#知识检索阶段的知识字典整体结构
knowl = {
    # domain
    "factual": {
        # Retrieving knowledge from
        "wikidata": 'some knowledge',
        "wikipedia": 'some knowledge',
    },
    "medical": {
        "uptodate": 'some knowledge',
    },
}

#编辑后的理由提示的结构
'''
Strictly follow the format of the below examples. The given sentence may have factual errors, please correct them based on the given external knowledge.
Sentence: the Alpher-Bethe-Gamow paper was invented by Ralph Alpher.
Knowledge: discoverer or inventor of Alpher-Bethe-Famow paper is Ralph Alpher. 
Edited sentence: the Alpher-Bethe-Gamow paper was invented by Ralph Alpher.

Sentence: Ralph Alpher was advised by Hans Bethe.
Knowledge: doctoral advisor of Ralph Alpher is George Gamow.
Edited sentence: Ralph Alpher was advised by George Gamow.

sentence: {rationale} #理由
Knowledge: {knowledge1} {knowledge2} {knowledge3} {knowledge4} #从knowl中获取的知识
Edited sentence: 
'''

