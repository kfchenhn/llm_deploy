import sys
import requests
import time

def send_request():
    url = 'http://10.254.25.12:8777/api/local_doc_qa/local_doc_chat'
    headers = {
        'content-type': 'application/json'
    }
    data = {
        "user_id": "zzp",
        "kb_ids": ["KB302083ae5773433885a3cca2cd7fc9ca"],
        "question": "RAG前沿技术",
        "networking":True
    }
    try:
        start_time = time.time()
        response = requests.post(url=url, headers=headers, json=data, timeout=60)
        end_time = time.time()
        res = response.json()#如果是流式返回的是数组不能直接转json
        print(res['response'])
        print(f"tokens:{res['tokens']}")
        print(f"响应状态码: {response.status_code}, 响应时间: {end_time - start_time}秒")
    except Exception as e:
        print(f"请求发送失败: {e}")


if __name__ == '__main__':
    send_request()