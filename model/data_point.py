
data_point={
  "question": '' , #问题
  "answer": '' , #数据集的答案
  "id": 0, #编号
  "s1_domains": [], #问题的领域
  "cot_response": '', #第一个的完整回答
  "cot_answer": '', #第一个回答中的答案
  "cot_sc_score": '', #分数，五个回答中次数最多的答案的占比
  "cot_sc_response": '', #次数最多的那次回答的完整回答
  "cot_sc_answer": '', #次数最多的那次回答中的答案
  "cot_sc_rationales": ['rationale_1','rationale_2'], #次数最多的那次回答中的理由1，理由2
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