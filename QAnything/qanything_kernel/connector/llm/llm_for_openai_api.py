from abc import ABC
import tiktoken
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional, List
import sys
import json
import requests
from qanything_kernel.utils.custom_log import debug_logger
sys.path.append("../../../")
from qanything_kernel.connector.llm.base import (BaseAnswer, AnswerResult)
from qanything_kernel.configs.model_config import CHATGLM_URL,CHATGPT_URL,QWEN_URL, WHUCSMed_URL, SYSTEM_MESSAGE, HUATUOGPT2_URL, LLM_HISTORY_LEN

load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
# OPENAI_API_MODEL_NAME = os.getenv("OPENAI_API_MODEL_NAME")
# OPENAI_API_CONTEXT_LENGTH = os.getenv("OPENAI_API_CONTEXT_LENGTH")
# if isinstance(OPENAI_API_CONTEXT_LENGTH, str) and OPENAI_API_CONTEXT_LENGTH != '':
#     OPENAI_API_CONTEXT_LENGTH = int(OPENAI_API_CONTEXT_LENGTH)
# debug_logger.info(f"OPENAI_API_BASE = {OPENAI_API_BASE}")
# debug_logger.info(f"OPENAI_API_MODEL_NAME = {OPENAI_API_MODEL_NAME}")


class OpenAILLM(BaseAnswer, ABC):
    model: str = None
    token_window: int = None
    max_token: int = 512
    offcut_token: int = 50
    truncate_len: int = 50
    temperature: float = 0
    top_p: float = 1.0 # top_p must be (0,1]
    stop_words: str = None
    history: List[List[str]] = []
    history_len: int = LLM_HISTORY_LEN
    api_key:str = None

    def __init__(self, args):
        super().__init__()
        base_url = args.openai_api_base
        self.api_key = args.openai_api_key

        self.qwen = OpenAI(base_url=QWEN_URL,api_key = self.api_key)
        self.chatglm3_6b = OpenAI(base_url=CHATGLM_URL,api_key = self.api_key)
        self.gpt = OpenAI(base_url=CHATGPT_URL,api_key = self.api_key)
        self.whucs_med_7b = OpenAI(base_url=WHUCSMed_URL,api_key = self.api_key)
        self.whucs_med_13b = OpenAI(base_url=HUATUOGPT2_URL,api_key = self.api_key)

        self.client = OpenAI(base_url=base_url, api_key=self.api_key)
        self.model = args.openai_api_model_name
        self.token_window = int(args.openai_api_context_length)
        debug_logger.info(f"OPENAI_API_KEY = {self.api_key}")
        debug_logger.info(f"OPENAI_API_BASE = {base_url}")
        debug_logger.info(f"OPENAI_API_MODEL_NAME = {self.model}")
        debug_logger.info(f"OPENAI_API_CONTEXT_LENGTH = {self.token_window}")


    @property
    def _llm_type(self) -> str:
        return "using OpenAI API serve as LLM backend"

    @property
    def _history_len(self) -> int:
        return self.history_len

    def set_history_len(self, history_len: int = 10) -> None:
        self.history_len = history_len

    # def switch_llm(self,model_name):
    #     if model_name == self.model :
    #         print(f"当前模型为{model_name},无需切换")
    #     elif model_name =="chatglm3-6b":
    #         self.client = self.chatglm3_6b
    #         print(f"切换模型{self.model}至{model_name}")
    #         debug_logger.info(f"切换模型{self.model}至{model_name}")
    #         self.model = "chatglm3-6b"
    #     elif model_name =="qwen":
    #         self.client = self.qwen
    #         print(f"切换模型{self.model}至{model_name}")
    #         debug_logger.info(f"切换模型{self.model}至{model_name}")
    #         self.model = "qwen"
    #     elif model_name =="whucs-med-7b":
    #         self.client = self.whucs_med_7b
    #         print(f"切换模型{self.model}至{model_name}")
    #         debug_logger.info(f"切换模型{self.model}至{model_name}")
    #         self.model = "whucs-med-7b"

    #     elif model_name.startswith("gpt"):
    #         self.client = self.gpt
    #         print(f"切换模型{self.model}至{model_name}")
    #         debug_logger.info(f"切换模型{self.model}至{model_name}")
    #         self.model = model_name
    # 定义函数 num_tokens_from_messages，该函数返回由一组消息所使用的token数
    def num_tokens_from_messages(self, messages, model=None):
        """Return the number of tokens used by a list of messages. From https://github.com/DjangoPeng/openai-quickstart/blob/main/openai_api/count_tokens_with_tiktoken.ipynb"""
        # debug_logger.info(f"[debug] num_tokens_from_messages<model, self.model> = {model, self.model}")
        if model is None:
            model = self.model
        # 尝试获取模型的编码
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # 如果模型没有找到，使用 cl100k_base 编码并给出警告
            debug_logger.info("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        # 针对不同的模型设置token数量
        if model in {
            "gpt-3.5-turbo-0613",
            # "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            "gpt-4-32k",
            # "gpt-4-1106-preview",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # 每条消息遵循 {role/name}\n{content}\n 格式
            tokens_per_name = -1  # 如果有名字，角色会被省略
        elif "gpt-3.5-turbo" in model:
            # 对于 gpt-3.5-turbo 模型可能会有更新，此处返回假设为 gpt-3.5-turbo-0613 的token数量，并给出警告
            debug_logger.info("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            # 对于 gpt-4 模型可能会有更新，此处返回假设为 gpt-4-0613 的token数量，并给出警告
            debug_logger.info("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")

        else:
            #debug_logger.info("孩子们这并不好笑")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
            # # 对于没有实现的模型，抛出未实现错误
            # raise NotImplementedError(
            #     f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            # )
            
        num_tokens = 0
        # 计算每条消息的token数
        for message in messages:
            if isinstance(message, dict):
                num_tokens += tokens_per_message
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":
                        num_tokens += tokens_per_name
            elif isinstance(message, str):
                num_tokens += len(encoding.encode(message))
            else:
                NotImplementedError(
                f"""num_tokens_from_messages() is not implemented message type {type(message)}. """
            )

        num_tokens += 3  # 每条回复都以助手为首
        return num_tokens

    def num_tokens_from_docs(self, docs):
        
        # 尝试获取模型的编码
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # 如果模型没有找到，使用 cl100k_base 编码并给出警告
            debug_logger.info("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        num_tokens = 0
        for doc in docs:
            num_tokens += len(encoding.encode(doc.page_content, disallowed_special=()))
        return num_tokens

    async def _call(self, prompt: str, history: List[List[str]], streaming: bool=False, model_name: str=None) -> str:
        messages = []
        MODEL = self.model
        if model_name == None:
            CLIENT = self.client
        elif model_name == "llm-only-for-rag-7b":
            CLIENT = self.qwen
            MODEL = "Qwen-7B-QAnything"
        elif model_name == "chatglm3-6b":
            CLIENT = self.chatglm3_6b
            MODEL = "chatglm3-6b"
        elif model_name == "whucs-med-7b":
            CLIENT = self.whucs_med_7b
            MODEL = "Apollo-7B"
        elif model_name == "whucs-med-13b":
            CLIENT = self.whucs_med_13b
            MODEL = "HuatuoGPT2-13B"
        elif model_name.startswith("gpt"):
            CLIENT = self.gpt
            MODEL = model_name
        else: 
            debug_logger.info(f"{model_name}不支持,切换至服务器当前大模型{self.model}" )
            print(f"{model_name}不支持,切换至服务器当前大模型{self.model}")
            CLIENT = self.client
        # if model_name !=None:
        #     MODEL = model_name
        
        current_history=[]
        if len(history) <= self.history_len:
            current_history=history
        else:
            current_history=history[-self.history_len:]

        for pair in current_history:
            #luzhuoran 移植本地模型对于history的策略
            if(len(pair)==0):
                break
            question, answer = pair
            messages.append({"role": "user", "content": question})
            messages.append({"role": "assistant", "content": answer})
        messages.append({"role": "user", "content": prompt})
        # chenkunfeng 加入 身份提示
        messages.append({"role": "system", "content": SYSTEM_MESSAGE})
        debug_logger.info(messages)

        try:

            if streaming:
                response = CLIENT.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    stream=True,
                    max_tokens=self.max_token,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    stop=[self.stop_words] if self.stop_words is not None else None,
                )
                debug_logger.info(f"OPENAI RES: {response}")
                for event in response:
                    if not isinstance(event, dict):
                        event = event.model_dump()

                    if isinstance(event['choices'], List) and len(event['choices']) > 0 :
                        event_text = event["choices"][0]['delta']['content']
                        if isinstance(event_text, str) and event_text != "":
                            # debug_logger.info(f"[debug] event_text = [{event_text}]")
                            delta = {'answer': event_text}
                            yield "data: " + json.dumps(delta, ensure_ascii=False)
                yield f"data: [DONE]\n\n"

            else:
                response = CLIENT.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    stream=False,
                    max_tokens=self.max_token,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    stop=[self.stop_words] if self.stop_words is not None else None,
                )
                
                debug_logger.info(f"[debug] response.choices = [{response.choices}]")
                event_text = response.choices[0].message.content if response.choices else ""
                delta = {'answer': event_text}
                yield "data: " + json.dumps(delta, ensure_ascii=False)

        except Exception as e:
            debug_logger.info(f"Error calling OpenAI API: {e}")
            delta = {'answer': f"{e}"}
            yield "data: " + json.dumps(delta, ensure_ascii=False)

        # finally:
        #     # debug_logger.info("[debug] try-finally")
        #     yield f"data: [DONE]\n\n"

    async def generatorAnswer(self, prompt: str,
                        history: List[List[str]] = [],
                        streaming: bool = False,
                        model_name: str = None) -> AnswerResult:

        if history is None or len(history) == 0:
            history = [[]]
        debug_logger.info(f"history_len: {self.history_len}")
        debug_logger.info(f"prompt: {prompt}")
        debug_logger.info(f"prompt tokens: {self.num_tokens_from_messages([{'content': prompt}])}")
        debug_logger.info(f"streaming: {streaming}")
                
        response = self._call(prompt, history, streaming, model_name)
        complete_answer = ""
        async for response_text in response:

            if response_text:
                chunk_str = response_text[6:]
                if not chunk_str.startswith("[DONE]"):
                    chunk_js = json.loads(chunk_str)
                    complete_answer += chunk_js["answer"]
                    
            history[-1] = [prompt, complete_answer]
 #           debug_logger.info(f"history-1:{history[-1]}")
            answer_result = AnswerResult()
            answer_result.history = history
            answer_result.llm_output = {"answer": response_text}
            answer_result.tokens = self.num_tokens_from_messages([{'content': prompt}])
            answer_result.prompt = prompt
            debug_logger.info(f"generatorAnswer response:{answer_result.llm_output}")
            yield answer_result


# if __name__ == "__main__":

#     llm = OpenAILLM()
#     streaming = True
#     chat_history = []
#     prompt = "你是谁"
#     prompt = """参考信息：
# 中央纪委国家监委网站讯 据山西省纪委监委消息：山西转型综合改革示范区党工委副书记、管委会副主任董良涉嫌严重违纪违法，目前正接受山西省纪委监委纪律审查和监察调查。\\u3000\\u3000董良简历\\u3000\\u3000董良，男，汉族，1964年8月生，河南鹿邑人，在职研究生学历，邮箱random@xxx.com，联系电话131xxxxx909，1984年3月加入中国共产党，1984年8月参加工作\\u3000\\u3000历任太原经济技术开发区管委会副主任、太原武宿综合保税区专职副主任，山西转型综合改革示范区党工委委员、管委会副主任。2021年8月，任山西转型综合改革示范区党工委副书记、管委会副主任。(山西省纪委监委)
# ---
# 我的问题或指令：
# 帮我提取上述人物的中文名，英文名，性别，国籍，现任职位，最高学历，毕业院校，邮箱，电话
# ---
# 请根据上述参考信息回答我的问题或回复我的指令。前面的参考信息可能有用，也可能没用，你需要从我给出的参考信息中选出与我的问题最相关的那些，来为你的回答提供依据。回答一定要忠于原文，简洁但不丢信息，不要胡乱编造。我的问题或指令是什么语种，你就用什么语种回复,
# 你的回复："""
#     final_result = ""
#     for answer_result in llm.generatorAnswer(prompt=prompt,
#                                                       history=chat_history,
#                                                       streaming=streaming):
#         resp = answer_result.llm_output["answer"]
#         if "DONE" not in resp:
#             final_result += json.loads(resp[6:])["answer"]
#         debug_logger.info(resp)

#     debug_logger.info(f"final_result = {final_result}")