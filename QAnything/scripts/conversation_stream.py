import os
import json
import requests
import time
import random
import string
import argparse

def stream_requests(data_raw):
    url = 'http://10.254.25.12:9999/api/local_doc_qa/local_doc_chat'
    response = requests.post(
        url,
        json=data_raw,
        timeout=60,
        stream=True
    )
    for line in response.iter_lines(decode_unicode=False, delimiter=b"\n\n"):
        if line:
            yield line

def test():
    data_raw = {
      "kb_ids": ["KB302083ae5773433885a3cca2cd7fc9ca"],
      "question": "RAG发展概况",
      "user_id": "zzp",
      "streaming": True,
      "history": []
    }
    
    for i, chunk in enumerate(stream_requests(data_raw)):
        if chunk:
            chunkstr = chunk.decode("utf-8")[6:]
            chunkjs = json.loads(chunkstr)
            print(chunkjs)

if __name__ == '__main__':
    test()