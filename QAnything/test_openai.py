import openai

openai.api_key = "EMPTY"
openai.base_url = "http://localhost:8001/v1/"

model = "Apollo-7B"
prompt = "Once upon a time"

# create a completion
completion = openai.completions.create(model=model, prompt=prompt, max_tokens=64)
# print the completion
print(prompt + completion.choices[0].text)

# create a chat completion
completion = openai.chat.completions.create(
  model=model,
  messages=[{"role": "user", "content": "Hello! What is your name?"}]
)
# print the completion
print(completion.choices[0].message.content)