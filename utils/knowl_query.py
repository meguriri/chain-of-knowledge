from utils.retrieval.wikidata import retrieve_wikidata_knowledge
# from utils.retrieval.wikitable import retrieve_wikitable_knowledge
from utils.retrieval.dpr import retrieve_dpr_knowledge
from utils.retrieval.wikipedia import retrieve_wikipedia_knowledge

from utils.retrieval.flashcard import retrieve_flashcard_knowledge
from utils.retrieval.uptodate import retrieve_uptodate_knowledge

from utils.retrieval.scienceqa_bio import retrieve_scienceqa_bio_knowledge
from utils.retrieval.ck12 import retrieve_ck12_knowledge

from utils.retrieval.scienceqa_phy import retrieve_scienceqa_phy_knowledge
from utils.retrieval.physicsclassroom import retrieve_physicsclassroom_knowledge

# domain and knowledge sources mapping
domain_mapping = {
    "factual": {
        "wikidata": retrieve_wikidata_knowledge,  # llama-2-7b-sparql-8bit->SPARQL
        # "dpr": retrieve_dpr_knowledge, # wiki_dpr,psgs_w100.multiset.compressed
        "wikipedia": retrieve_wikipedia_knowledge,  # serpAPI->googleSearch ✅
    },
    "medical": {
        # "flashcard": retrieve_flashcard_knowledge,  # llama-2-7b-medical-flashcards-8bit
        "uptodate": retrieve_uptodate_knowledge,  # serpAPI->googleSearch ✅
    },
    "biology": {
        "scienceqa_bio": retrieve_scienceqa_bio_knowledge,  # llama-2-7b-biology-scienceqa-8bit
        "ck12": retrieve_ck12_knowledge,  # serpAPI->googleSearch ✅
    },
    "physical": {
        "scienceqa_phy": retrieve_scienceqa_phy_knowledge,  # llama-2-7b-physics-scienceqa-8bit
        "physicsclassroom": retrieve_physicsclassroom_knowledge,  # serpAPI->googleSearch ✅
    },
}

'''
检索知识：
domain: 域,
input: 输入的理由,
data_point: 一个样本,
'''


def retrieve_knowledge(domain, input, data_point):
    # input is a string
    # 域的字典
    knowl = {}
    # If not in mapping, automatically use "factual"
    # 修改知识域，将没有收集的域更改为factual（事实）
    domain = [x if x in domain_mapping else "factual" for x in domain]
    # Remove duplicates
    # 将重复的域删除
    domain = list(dict.fromkeys(domain))

    # 遍历域
    for x in domain:
        # 将域作为key对应一个知识获取函数的字典
        knowl[x] = {}
        # 获取对应域的资源字典
        domain_sources = domain_mapping[x]
        # 遍历资源字典的key
        for y in domain_sources:
            print("--- Retrieving knowledge from", x, y)
            # 得到该域对应资源的知识获取函数，传入理由input和数据样本data_point，将调用结果存入knowl中
            tmp_knowl = domain_sources[y](input, data_point)
            # print(tmp_knowl)
            # 将该函数存到
            knowl[x][y] = tmp_knowl

    # 返知识获取结果字典
    return knowl


def knowl_is_empty(knowl):
    for x in knowl:
        for y in knowl[x]:
            if knowl[x][y] != '':
                return False
    return True
