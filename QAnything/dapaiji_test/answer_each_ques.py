import pandas as pd
import requests
import json
from tqdm import tqdm
import csv

import time

# 调用RAG接口(对话接口)
def send_request_rag_chat(question,kb_ids_list,model_name):
    url = 'http://localhost:8777/api/local_doc_qa/local_doc_chat'
    headers = {
        'content-type': 'application/json'
    }
    data = {
        "user_id": "zzp",
        "kb_ids": kb_ids_list,
        "question": question,
        "model": model_name
    }
    try:
        response = requests.post(url=url, headers=headers, json=data, timeout=60)
        res = response.json()
        json_answer = res['response'].split('data: ')[1]
        parsed_data = json.loads(json_answer)
        answer_text = parsed_data.get('answer', '')
        return answer_text

    except Exception as e:
        print(f"请求发送失败: {e}")


def send_request_list_kbs():
    url = 'http://localhost:8777/api/local_doc_qa/list_knowledge_base'
    headers = {
        'content-type': 'application/json'
    }
    data = {
        "user_id": "zzp",
    }
    try:
        response = requests.post(url=url, headers=headers, json=data, timeout=60)
        res = response.json()
        json_answer = res['data']
        # answer_text = parsed_data.get('answer', '')
        return json_answer

    except Exception as e:
        print(f"请求发送失败: {e}")


def csv_to_dict_list(file_path):
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        dict_list = [row for row in csv_reader]
        return dict_list

def dict_list_to_json(dict_list, json_file_path):
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(dict_list, json_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # list_available_models = ["whucs-med-7b","whucs-med-13b","gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613","llm-only-for-rag-7b"]
    # {'kb_id': 'KBbde081f1d240418ea1a1d410dc250d30', 'kb_name': '邓学东-产前超声诊断与鉴别诊断 妊娠诊断'}, {'kb_id': 'KB948fd3c5801140679d33cc63c7c032aa', 'kb_name': '李胜利-胎儿畸形产前超声诊断学'}, {'kb_id': 'KB5fc35121f03b40b991643f3cba5f1953', 'kb_name': '任芸芸-中国产科超声检查指南'}, {'kb_id': 'KBff5c230eab704af0850caf0ce3087346', 'kb_name': '吴乃森-产前超声诊断与鉴别诊断学'}
    all_kb_ids_list = ['KBbde081f1d240418ea1a1d410dc250d30','KB948fd3c5801140679d33cc63c7c032aa', 'KB5fc35121f03b40b991643f3cba5f1953', 'KBff5c230eab704af0850caf0ce3087346']
    kb_ids_list = []
    model_name = 'whucs-med-7b'

    csv_file = '/home/c205/workspace/QAnything/dapaiji_test/大排畸中的小问题.csv'
    result_csv_file = '/home/c205/workspace/QAnything/dapaiji_test/大排畸中的小问题-测试结果-2.csv'
    qa_list = csv_to_dict_list(csv_file)
    
    test_result_list = []
    for qa_item in tqdm(qa_list):
        
        question = qa_item['question']
        gt_answer = qa_item['ground truth answer']

        answer_7b = send_request_rag_chat(question,kb_ids_list, 'whucs-med-7b')
                
        qa_item['answer_of_7b_model'] = answer_7b
        
        test_result_list.append(qa_item)
        print(qa_item)
    time.sleep(10)

    # for qa_item in tqdm(test_result_list):
        
    #     question = qa_item['question']
    #     gt_answer = qa_item['ground truth answer']

    #     answer_13b = send_request_rag_chat(question,kb_ids_list, 'whucs-med-13b')

    #     qa_item['answer_of_13b_model'] = answer_13b

    #     test_result_list.append(qa_item)
    #     print(qa_item)

    # time.sleep(10)
    
    # for qa_item in tqdm(test_result_list):
        
    #     question = qa_item['question']
    #     gt_answer = qa_item['ground truth answer']

    #     answer_rag = send_request_rag_chat(question,all_kb_ids_list, 'llm-only-for-rag-7b')

    #     qa_item['answer_of_rag_model'] = answer_rag

    #     test_result_list.append(qa_item)
    #     print(qa_item)
    
    dict_list_to_json(test_result_list,result_csv_file)
