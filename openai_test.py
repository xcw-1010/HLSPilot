import os
import re
import ast
import time
import openai

from prompt.prompt_api_test import BASELINE_PROMPT, PIPELINE_PROMPT_1, PIPELINE_PROMPT_2, PIPELINE_PROMPT_3, TEST_PROMPT, OPT_CHOOSE_PROMPT_TEST2, DAG_GRAPH_PROMPT_TEST, TASK_PIPELINE_ADVICE_PROMPT, DETERMINE_CONTINUE_SPLIT_TEST, CONTINUE_SPLIT_TEST

from prompt.prompt_bfgs import TASK_PIPELINE_FOR_BFGS_1, TASK_PIPELINE_FOR_BFGS_2

from task_opt import parse_opt_list
from task_pipeline import *

openai.api_key = """ OPENAI API KEY """
# os.environ["HTTP_PROXY"] = "http://127.0.0.1:33210"
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:33210"

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

"""
token数计算: https://tiktoken.aigc2d.com/
"""

class chatGPT:
    def __init__(self, system):
        self.messages = [{"role": "system", "content": system}]
    
    def get_chat_response(self):
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview", 
            messages=self.messages
        )
        return response.choices[0]["message"]["content"]

def extract_content_and_save(chat_completion, chat_file_path, code_file_path):
    with open(chat_file_path, 'w') as chat_file:
        chat_file.write(str(chat_completion))

    msg = chat_completion.choices[0].message
    content = msg["content"]
    match = re.search(r"\`\`\`(.*?)\`\`\`", content, re.DOTALL)
    if match:
        code_content = match.group(1)
        print(code_content)
        with open(code_file_path, 'w') as code_file:
            code_file.write(code_content)


if __name__ == '__main__':
    # api call: 
    # model_list = ["gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"]
    chat_completion = openai.ChatCompletion.create(
        model="gpt-4-1106-preview", 
        messages=[{
          "role": "user", 
          "content": "hello"}])
    print(chat_completion.choices[0].message)
    print(chat_completion)

    # multiple turn chat: 
    # system = "an FPGA engineer"
    # chat = chatGPT(system)
    # while len(chat.messages) < 5:
    #     print(chat.messages)
    #     user_content = input()
    #     chat.messages.append({"role": "user", "content": user_content})
    #     response = chat.get_chat_response()
    #     print(response)
    #     chat.messages.append({"role": "assistant", "content": response})
