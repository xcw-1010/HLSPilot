import os
import re
import time
import openai
from openai import OpenAI

from prompt.prompt import SYSTEM_PROMPT, TASK_PIPELINE_PROMPT, TASK_PIPELINE_STRATEGY_PROMPT, TASK_PIPELINE_STRATEGY_PROMPT_4, TASK_PIPELINE_FOR_SINGLE_FUNCTION_PROMPT

root_path = "./"
benchmark_dir = "./benchmark"
pipeline_log_path = "./log/pipeline"

openai.api_key = """ OPENAI API KEY """

# split the whole code
def gen_task_pipeline_prompt(algo_name, func_description):
    _SYSTEM_PROMPT = SYSTEM_PROMPT.replace("{ALGO_NAME}", algo_name)
    _SYSTEM_PROMPT = _SYSTEM_PROMPT.replace("{FUNCTION_DESCRIPTION}", func_description)

    code_path = f"{benchmark_dir}/{algo_name}/{algo_name}.cpp"
    with open(code_path, "r") as code_file:
        CODE = "\n" + code_file.read()

    TASK_PIPELINE_PROMPT_COMPLETE = _SYSTEM_PROMPT + TASK_PIPELINE_PROMPT + CODE
    TASK_PIPELINE_PROMPT_COMPLETE += TASK_PIPELINE_STRATEGY_PROMPT_4 # add strategy hint
    print(TASK_PIPELINE_PROMPT_COMPLETE)
    return TASK_PIPELINE_PROMPT_COMPLETE


# split sub function in the code
def gen_sub_task_pipeline_prompt(algo_name, func_description, func_content):
    _SYSTEM_PROMPT = SYSTEM_PROMPT.replace("{ALGO_NAME}", algo_name)
    _SYSTEM_PROMPT = _SYSTEM_PROMPT.replace("{FUNCTION_DESCRIPTION}", func_description)

    TASK_PIPELINE_PROMPT_COMPLETE = _SYSTEM_PROMPT + TASK_PIPELINE_FOR_SINGLE_FUNCTION_PROMPT + func_content
    TASK_PIPELINE_PROMPT_COMPLETE += TASK_PIPELINE_STRATEGY_PROMPT_4 # add strategy hint
    print(TASK_PIPELINE_PROMPT_COMPLETE)
    return TASK_PIPELINE_PROMPT_COMPLETE


def extract_content_and_save(chat_completion, prompt_content, model_name, algo_name, sub_func=False):
    if model_name in ["gpt-4-1106-preview", "gpt-4"]:
        model_name = "gpt4"
    else:
        model_name = "gpt3.5"
    cur_time = time.strftime('%y%m%d_%H%M', time.localtime())
    chat_file_path = f"{pipeline_log_path}/{model_name}/{algo_name}/pipeline_{model_name}_{algo_name}_{cur_time}.txt"
    code_file_path = f"{pipeline_log_path}/{model_name}/{algo_name}/pipeline_{model_name}_{algo_name}_{cur_time}.cpp"

    if sub_func:
        chat_file_path = f"{pipeline_log_path}/{model_name}/{algo_name}/sub_pipeline_{model_name}_{algo_name}_{cur_time}.txt"
        code_file_path = f"{pipeline_log_path}/{model_name}/{algo_name}/sub_pipeline_{model_name}_{algo_name}_{cur_time}.cpp"

    # save chat completion
    with open(chat_file_path, 'w') as chat_file:
        chat_file.write(str(chat_completion))
        chat_file.write("\n\n====================================\n\n")
        chat_file.write(prompt_content)

    # extract code from ``` ``` and save
    content = chat_completion.choices[0].message["content"]
    match = re.search(r"\`\`\`(.*?)\`\`\`", content, re.DOTALL)
    if match:
        code_content = match.group(1)
        print(code_content)
        with open(code_file_path, 'w') as code_file:
            code_file.write(code_content)


def run_task_pipeline(algo_name, func_description):
    prompt = gen_task_pipeline_prompt(algo_name, func_description)
    model_name = "gpt-4-1106-preview"
    task_pipeline_completion = openai.ChatCompletion.create(model=model_name, messages=[{
        "role": "user", 
        "content": prompt}])
    print(task_pipeline_completion)
    extract_content_and_save(task_pipeline_completion, prompt, model_name, algo_name)


def run_sub_task_pipeline(algo_name, func_description, func_content):
    prompt = gen_sub_task_pipeline_prompt(algo_name, func_description, func_content)
    model_name = "gpt-4-1106-preview"
    sub_task_pipeline_completion = openai.ChatCompletion.create(model=model_name, messages=[{
        "role": "user", 
        "content": prompt}])
    print(sub_task_pipeline_completion)
    extract_content_and_save(sub_task_pipeline_completion, prompt, model_name, algo_name, sub_func=True)


def connection_test():
    prompt = "hello"
    model_name = "gpt-4-1106-preview"
    test_completion = openai.ChatCompletion.create(model=model_name, messages=[{
        "role": "user", 
        "content": prompt}])
    print(test_completion)

algo_name_list = ["bfs", "cc", "dft", "fft", "fir", "histogram", "huffman", "insert_sort", "matrix_multiplication", "merge_sort", "pagerank", "prefix_sum", "spmv", "sssp"]
# gen_task_pipeline_prompt("pagerank", "pagerank algorithm")

if __name__ == "__main__":
    algo_name = "bfs"
    func_description = "bfs algorithm"
    func_content = \
"""
void explore_neighbors(const int *rpao, const int *ciao, int *labels, int *queue, int &front, int &rear) {
    if (front == -1) {
        return; // No more vertices to process
    }
    int cur_idx = queue[front++];

#pragma HLS PIPELINE II=1
    int start = rpao[cur_idx];
    int end   = rpao[cur_idx + 1];

    for (int j = start; j < end; ++j) {
#pragma HLS LOOP_FLATTEN off
#pragma HLS PIPELINE II=1
        int ngb_idx = ciao[j];
        if (labels[ngb_idx] == -1) {
            labels[ngb_idx] = labels[cur_idx];
            queue[rear++] = ngb_idx;
        }
    }

    if (front == rear) {
        front = -1; // Completed processing current component
    }
}
"""
    run_task_pipeline(algo_name, func_description)
    # run_sub_task_pipeline(algo_name, func_description, func_content)
    # connection_test()


