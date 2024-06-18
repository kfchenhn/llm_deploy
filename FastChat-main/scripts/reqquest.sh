
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{ \
    "model": "vicuna-7b-v1.5", \
    "messages": [{"role": "user", "content": "Hello, can you tell me a joke for me?"}], \
    "temperature": 0.5 \
  }'