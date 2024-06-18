import requests
import json

url = "http://10.254.25.12:8777/api/local_doc_qa/update_bot"
headers = {
    "Content-Type": "application/json"
}
data = {
    "user_id": "zzp",
    "bot_id": "BOT284f59908e4e45598efe9c8b15de46d9",
    "bot_name": "测试Bot2",
    "description": "测试3",
    "prompt_setting": "测试4",
    "welcome_message": "测试5",
    "model": "MiniChat-2-3B",
    "kb_ids": ["KB461d08475b9548aaab37c843544bb111"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)