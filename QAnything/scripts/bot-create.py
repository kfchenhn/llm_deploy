import requests
import json

url = "http://10.254.25.12:8777/api/local_doc_qa/new_bot"
headers = {
    "Content-Type": "application/json"
}
data = {
	"user_id": "zzp",
	"bot_name": "测试机器人",
    "prompt_setting":"你叫hhb，是一位百度贴吧用户，擅长打🦌",
    "description":"hhhhhhh",
    "kb_ids":["KB461d08475b9548aaab37c843544bb111"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)