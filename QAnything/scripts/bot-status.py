import requests
import json

url = "http://10.254.25.12:8777/api/local_doc_qa/get_bot_info"
headers = {
    "Content-Type": "application/json",
}
data = {
	"user_id": "zzp",
}

response = requests.post(url, headers=headers, data=json.dumps(data))
response.encoding = 'utf-8'
print(type(response))
print(response.status_code)
print(json.loads(response.text))