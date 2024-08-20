import argparse #命令行参数
import json #json解析
from pathlib import Path #路径解析

from tqdm import tqdm #进度条

#openAI utils
from utils.openai_utils import call_openai_api

#不同数据集的提示 utils
from utils.other_prompts import domain_selection_demonstration

# FetaQA的数据集utils（wiki）
from utils.fetaqa_eval import main as fetaqa_eval

# init gloabl variables
import utils.globalvar
utils.globalvar.init()

import os

'''
推理准备阶段:
dataset: 数据集,
data_point: 一条QA,
model: gpt模型类型,
threshold: , ##TODO 阈值？？
''' 
def s1_reasoning_preparation(dataset, data_point, model, threshold):
    print("****************** Start stage 1: reasoning preparation ...")

    #获取问题
    question = dataset.get_question(data_point)
    print("****** Question:", question)

    ### Domain selection
    # 选择提示的域
    # domain_selection_demonstration 域的选择（强制gpt选择问题的域）;question.strip():去除问题头尾空格;
    domain_selection_prompt = domain_selection_demonstration + "Q: " + question.strip() + "\nRelevant domains: "
    #获取gpt的response
    domain_selection_response = call_openai_api(model, domain_selection_prompt, max_tokens=256, temperature=0)
    
    if domain_selection_response is not None:
        domain_selection_text_response = domain_selection_response[1].strip()
        print("****** Relevant domains:", domain_selection_text_response)
        data_point["s1_domains"] = [x.strip() for x in domain_selection_text_response.split(",")]
    
    ### CoT generation
    cot_prompt = dataset.get_s1_prompt(question)
    
    data_point = dataset.get_cot_sc_results(data_point, model, cot_prompt)
    print("****** CoT answer:", data_point["cot_response"])
    print("****** CoT SC score:", data_point["cot_sc_score"])
    print("****** CoT SC answer:", data_point["cot_sc_response"])

    return data_point


def s2_knowledge_adapting(dataset, data_point, model, step):
    print("****************** Start stage 2: knowledge adapting ...")
    if step:
        print("****** Edit mode: Step by step")
        # Edit the rationales step by step
        data_point = dataset.update_rationales_step_by_step(model, data_point)

    else:
        # Edit the rationales all at once
        print("****** Edit mode: At once")
        # Edit the rationales step by step
        data_point = dataset.update_rationales_at_once(model, data_point)

    return data_point

def s3_answer_consolidation(dataset, data_point, model):
    print("****************** Start stage 3: answer consolidation ...")
    data_point = dataset.get_final_answer(model, data_point)
    return data_point


if __name__ == "__main__":
    # read arguments
    parser = argparse.ArgumentParser()
    #定义命令行参数
    # gpt模型类型
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-0613", help="OpenAI API model name")
    parser.add_argument("--dataset", type=str, help="Dataset name")
    parser.add_argument("--output", type=str, help="Output path")
    parser.add_argument("--step", type=bool, default=False, help="Whether to edit the rationales step by step")
    parser.add_argument("--num_train", type=int, default=3, help="How many demonstration samples to use")
    parser.add_argument("--num_test", type=int, default=5, help="How many test samples to use")
    parser.add_argument("--threshold", type=float, default=0.5, help="sc threshold for ka answer")
    parser.add_argument("--one_shot", action="store_true", help="Whether to use 1-shot setting")
    parser.add_argument("--six_shot", action="store_true", help="Whether to use 6-shot setting")

    #获取命令行参数
    args = parser.parse_args()
    
    # TODO: add other datasets, as well as a parser for each dataset
    # 判断数据集类型
    if args.dataset == "hotpotqa":
        from utils.hotpotqa_parser import hotpotqa
        #数据集为hotpotqa
        dataset = hotpotqa()
    elif args.dataset == "medmcqa":
        from utils.medmcqa_parser import medmcqa
        dataset = medmcqa()
    elif args.dataset == "mmluphy":
        from utils.phy_parser import phy
        dataset = phy()
    elif args.dataset == "mmlubio":
        from utils.bio_parser import bio
        dataset = bio()
    elif args.dataset == "fever":
        from utils.fever_parser import fever
        dataset = fever(six_shot=args.six_shot, one_shot=args.one_shot)
    elif "feta" in args.dataset:
        from utils.fetaqa_parser import select_fetaqa_dataset
        dataset = select_fetaqa_dataset(args.dataset, num_train=args.num_train)
    else:
        raise Exception("Invalid dataset name")

    # load data
    #创建输出文件
    Path(args.output).parent.mkdir(exist_ok=True, parents=True)
    #获取json数据
    data = dataset.get_dataset()
    print('original data length:', len(data))
    #输出文件已经存在
    if os.path.exists(args.output):
        print('Found existing outputs, will replace the original data with the existing outputs')
        # read existing outputs
        output_data = json.load(open(args.output, "r"))
        print('Found {} existing outputs'.format(len(output_data)))
        # replace the original data with the existing outputs
        replace_count = 0
        for d in output_data:
            for i in range(len(data)):
                if d['question'] == data[i]['question']:
                    data[i] = d
                    replace_count += 1
                    break
        print('replaced {} existing outputs'.format(replace_count))
        print('Found {} prepared outputs.'.format(len([x["id"] for x in data if 'cot_answer' in x])))
        print('Found {} outputs that need to be edited.'.format(len([x["id"] for x in data if 'cot_answer' in x and x["cot_sc_score"] < args.threshold and 'final_answer' not in x])))
        print('Found {} edited outputs.'.format(len([x["id"] for x in data if 'final_answer' in x])))
        
    
    count = 0 

    #遍历数据集或者自定义的数据大小
    for i in tqdm(range(min(args.num_test, len(data)))):
        print("####################################", i, "####################################")
        
        #每一个QA
        data_point = data[i]
        #为每一个QA添加一个id
        data_point["id"] = i

        # 数据集为fetaq或fetaqa——query的情况
        if args.dataset == "fetaqa" or args.dataset == "fetaqa_query":
            question = data_point["question"]
            cot_prompt = dataset.get_s1_prompt(question)
            data_point = dataset.get_cot_sc_results(data_point, args.model, cot_prompt)
            print("****** CoT answer:", data_point["cot_response"])
            print("****** CoT SC score:", data_point["cot_sc_score"])
            print("****** CoT SC answer:", data_point["cot_sc_response"])
            data[i] = data_point
            with open(args.output, "w") as f:
                json.dump(data, f)
            continue
        

        # add filtering to ensure we have not previously produced the results
        # 如果字典data_point中没有key：cot_sc_score
        if 'cot_sc_score' not in data_point:
            ##### run stage 1: reasoning preparation
            ##### 开始阶段1

            ##生成新的QA字典
            data_point = s1_reasoning_preparation(dataset, data_point, args.model, args.threshold)
            
            # update the datapoint
            # 更新数据
            data[i] = data_point
            
            # 将data结果以json形式，写入输出文件中
            with open(args.output, "w") as f:
                json.dump(data, f)
    
        # Self-consistency threshold
        if data_point["cot_sc_score"] < args.threshold and 'final_answer' not in data_point:
            # continue only when the score is lower than threshold
            ##### run stage 2: knowledge adapting
            data_point = s2_knowledge_adapting(dataset, data_point, args.model, args.step)

            # update the datapoint
            data[i] = data_point

            with open(args.output, "w") as f:
                json.dump(data, f)

            ##### run stage 3: answer consolidation
            data_point = s3_answer_consolidation(dataset, data_point, args.model)

            # update the datapoint
            data[i] = data_point

            with open(args.output, "w") as f:
                json.dump(data, f)
        else:
            count += 1
            continue

    if "feta" in args.dataset:
        fetaqa_eval(args.output)

    print("Number of skipped samples (high consistency): ", count)
    print("ALL DONE!!")

"""
p run.py --dataset fetaqa --output outputs/fetaqa_full.json --num_test 500
p run.py --dataset fetaqa --output outputs/fetaqa.json --num_test 100
p run.py --dataset fetaqa_editing --output outputs/fetaqa_editing.json --num_test 100 --step True --threshold 0.3
"""
