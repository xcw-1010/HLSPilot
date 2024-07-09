from langchain_core.tools import tool
from langchain_core.tools import StructuredTool
from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

import subprocess
import os

from hw_sw_partition_prompt import SYSTEM_PROMPT, CODE_ANALYSIS_PROMPT

""" enviroment set up """
os.environ["OPENAI_API_KEY"] = " OPENAI API KEY "
benchmark_path = "benchmark"

def generate_gprof_report(app, output_file='gprof.txt'):
    compile_command = f"g++ -pg -o {benchmark_path}/{app}/{app} {benchmark_path}/{app}/{app}.cpp"
    subprocess.run(compile_command, shell=True, check=True)

    run_command = f".\{benchmark_path}\{app}\{app}.exe"
    subprocess.run(run_command, shell=True, check=True)

    gprof_command = f"gprof {benchmark_path}/{app}/{app}.exe gmon.out > {benchmark_path}/{app}/{output_file}"
    subprocess.run(gprof_command, shell=True, check=True)

    report_path = benchmark_path + '/' + app + '/' + output_file
    with open(report_path, 'r') as file:
        report = file.read()
    return report

def analysis_report(app, report_content):
    PROMPT_COMPLETE = ""
    PROMPT_COMPLETE += SYSTEM_PROMPT.replace("{ALGO_NAME}", app)
    
    app_file_path = benchmark_path + '/' + app + '/' + app + '.cpp'
    with open(app_file_path, 'r') as app_file:
        code_content = app_file.read()

    _CODE_ANALYSIS_PROMPT = CODE_ANALYSIS_PROMPT.replace("{CODE_CONTENT}", code_content)
    _CODE_ANALYSIS_PROMPT = _CODE_ANALYSIS_PROMPT.replace("{REPORT_CONTENT}", report_content)
    
    PROMPT_COMPLETE += _CODE_ANALYSIS_PROMPT
    print(PROMPT_COMPLETE)

    chat_model = ChatOpenAI(model='gpt-4-1106-preview')
    messages = [
        HumanMessage(content=PROMPT_COMPLETE),
    ]
    response = chat_model.invoke(messages)
    print(response)


class AutoAnalysisInput(BaseModel):
    application: str = Field(description="application name")

class AutoAnalysisTool(BaseTool):
    name = "Auto Code Analysis Tool"
    description = "Used to call the gprof tool to generate performance reports, analyze the reports using LLM, and output various performance indicators"
    args_schema: Type[BaseModel] = AutoAnalysisInput
    return_direct: bool = True

    def _run(
        self, application: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        report_content = generate_gprof_report(application)
        analysis_report(application, report_content)

if __name__ == "__main__":
    mytool = AutoAnalysisTool()
    print(mytool.name)
    print(mytool.description)
    print(mytool.args)
    print(mytool.return_direct)
    print(mytool.invoke({"application": "test"}))