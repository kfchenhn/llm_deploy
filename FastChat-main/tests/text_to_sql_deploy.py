
import warnings

import openai
from fastchat.utils import run_cmd


openai.api_key = "EMPTY"  # Not support yet
openai.base_url = "http://10.254.25.43:8001/v1/"


def test_chat_completion(model):
    completion = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "哪个县的危化企业数量最多？"}],
        temperature=0,
    )
    print(completion.choices[0].message.content)



def test_openai_curl():
    run_cmd(
        """
curl http://10.254.25.43:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "txt2sql_merge_model",
    "messages": [{"role": "user", "content": "应入网企业在孝昌有多少家"}]
  }'
"""
    )


if __name__ == "__main__":
  
    model = "txt2sql_merge_model"

    test_chat_completion(model)
  
    print("===== Test curl =====")
    test_openai_curl()
