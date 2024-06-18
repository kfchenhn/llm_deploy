import os
import json
import requests
import time
import random
import string
import argparse

def stream_requests(data_raw):
    url = 'http://localhost:8777/api/local_doc_qa/local_doc_chat'
    response = requests.post(
        url,
        json=data_raw,
        timeout=60,
        stream=False
    )
    for line in response.iter_lines(decode_unicode=False, delimiter=b"\n\n"):
        if line:
            yield line

def test():
    data_raw = {"streaming":True,"question":"马应龙？",
                "user_id":"dhljtestuser","history":[["怎么改善油脂粒","使用马应龙八宝油脂粒眼霜可以改善油脂粒。该眼霜的主要成分为北非雪松树皮、广西沙柑果皮油、芦荟根提取物、霍霍巴籽油、香柠檬果油、珍珠粉、甘油、尿囊素等，这些成分都有助于补 水保湿、改善油脂粒。使用方法为在洁肤后，取适量眼霜按摩至吸收即可。"]],
                "bot_id":"BOT474a43f3ba01462a99eccaad6744764a",
#                "kb_ids":["KB4e9b3a8ff9464123a63b1dc9057f4897"],
                "model_name":"qwen"}
    for i, chunk in enumerate(stream_requests(data_raw)):
        if chunk:
            chunkstr = chunk.decode("utf-8")[6:]
            chunkjs = json.loads(chunkstr)
            print(chunkjs)

if __name__ == "__main__":
    test()