import requests
import json

url = "http://10.254.25.12:8777/api/switch_llm"
headers = {
    "Content-Type": "application/json"
}
data = {
    "model":"qwen"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.text)

#"gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613","chatglm3-6b" ,"qwen"