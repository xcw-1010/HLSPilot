import os
import re
import ast
import time
import openai

from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "xxx"

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
    client = OpenAI(
    # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
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
