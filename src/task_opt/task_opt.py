import os
import re
import time
import openai
from prompt.prompt import *
from task_pipeline import connection_test

openai.api_key = """ OPENAI API KEY """
os.environ["HTTP_PROXY"] = "http://127.0.0.1:33210"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:33210"

root_path = "D:/Code/HLSPilot"
opt_options = ["ALLOCATION", "RESOURCE", "INLINE", 
               "FUNCTION_INSTANTIATE", "STREAM", "PIPELINE", 
               "OCCURRENCE", "UNROLL", "DEPENDENCE", 
               "LOOP_FLATTEN", "LOOP_MERGE", "LOOP_TRIPCOUNT", 
               "ARRAY_MAP", "ARRAY_PARTITION", "ARRAY_RESHAPE", 
               "DATA_PACK"]
model_name = "gpt-4-1106-preview"

def gen_stage_opt_prompt(stage_code):
    STAGE_CODE_CONTENT = stage_code
    PRAGMA_DESCRIPTION = ""
    for opt in opt_options:
        prompt_name = f"{opt}_PROMPT"
        prompt_content = globals()[prompt_name]
        PRAGMA_DESCRIPTION += prompt_content
        PRAGMA_DESCRIPTION += "-----------------------"
    _OPT_CHOICE_PROMPT = OPT_CHOICE_PROMPT.replace("{PRAGMA_DESCRIPTION}", PRAGMA_DESCRIPTION)
    _OPT_CHOICE_PROMPT = _OPT_CHOICE_PROMPT.replace("{STAGE_CODE_CONTENT}", STAGE_CODE_CONTENT)
    print(_OPT_CHOICE_PROMPT)
    return _OPT_CHOICE_PROMPT

# completion_type: opt_choose or opt_apply
def save_chat_completion(completion_type, prompt_content, chat_completion, model_name):
    experiment_name = completion_type
    if model_name in ["gpt-4-1106-preview", "gpt-4"]:
        model_name = "gpt4"
    else:
        model_name = "gpt3.5"
    
    cur_time = time.strftime('%y%m%d_%H%M', time.localtime())
    chat_file_path = f"{root_path}/log/stage_opt/{model_name}/{experiment_name}_{model_name}_{cur_time}.txt"
    with open(chat_file_path, "w") as chat_file:
        chat_file.write(str(chat_completion))
        chat_file.write("\n\n====================================\n\n")
        chat_file.write(prompt_content)
    
    # extract code from ``` ``` and save
    if completion_type == "opt_apply":
        code_file_path = f"{root_path}/log/stage_opt/{model_name}/{experiment_name}_{model_name}_{cur_time}.cpp"
        content = chat_completion.choices[0].message["content"]
        match = re.search(r"\`\`\`(.*?)\`\`\`", content, re.DOTALL)
        if match:
            code_content = match.group(1)
            print(code_content)
            with open(code_file_path, 'w') as code_file:
                code_file.write(code_content)


def parse_opt_list(stage_opt_completion):
    raw_list_str = stage_opt_completion.choices[0].message["content"]
    raw_list_str = raw_list_str[1:-1]
    opt_list = raw_list_str.split(", ")
    return opt_list


def apply_opt(stage_code, stage_opt_list, algo_name, func_description):
    _SYSTEM_PROMPT = SYSTEM_PROMPT.replace("{ALGO_NAME}", algo_name)
    _SYSTEM_PROMPT = _SYSTEM_PROMPT.replace("{FUNCTION_DESCRIPTION}", func_description)
    
    STAGE_CODE_CONTENT = stage_code
    OPT_LIST = ""
    PRAGMA_DEMO_COMPLETE = ""

    opt_code = "xxx"
    for i, opt_option in enumerate(stage_opt_list):
        OPT_LIST += str(i) + ". " + opt_option + "\n"
        pragma_name = opt_option.split(" ")[-1].upper() + "_DEMO"
        PRAGMA_DEMO = globals()[pragma_name]
        PRAGMA_DEMO_COMPLETE += str(i) + ". " + opt_option + ":\n" + PRAGMA_DEMO + "\n"

    _APPLY_OPT_PROMPT = APPLY_OPT_PROMPT.replace("{STAGE_CODE_CONTENT}", STAGE_CODE_CONTENT)
    _APPLY_OPT_PROMPT = _APPLY_OPT_PROMPT.replace("{OPT_LIST}", OPT_LIST)
    _APPLY_OPT_PROMPT = _APPLY_OPT_PROMPT.replace("{PRAGMA_DEMO}", PRAGMA_DEMO_COMPLETE)

    STAGE_OPT_PROMPT_COMPLETE = _SYSTEM_PROMPT + _APPLY_OPT_PROMPT
    print(STAGE_OPT_PROMPT_COMPLETE)

    opt_apply_completion = openai.ChatCompletion.create(model=model_name, messages=[{
        "role": "user",
        "content": STAGE_OPT_PROMPT_COMPLETE}])
    print(opt_apply_completion)
    save_chat_completion("opt_apply", STAGE_OPT_PROMPT_COMPLETE, opt_apply_completion, model_name)
    return opt_code

"""
model_list = ["gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"]
"""
def run_stage_code_opt(stage_code):
    prompt = gen_stage_opt_prompt(stage_code)
    algo_name = "bfgs"
    func_description = "bfgs"
    stage_opt_completion = openai.ChatCompletion.create(model=model_name, messages=[{
        "role": "user", 
        "content": prompt}])
    print(stage_opt_completion)
    stage_opt_list = parse_opt_list(stage_opt_completion)
    save_chat_completion("opt_choose", prompt, stage_opt_completion, model_name)
    opt_code = apply_opt(stage_code, stage_opt_list, algo_name, func_description)
    return opt_code


if __name__ == "__main__":
    stage_code = \
"""
// Stage 1: Compute convolution and cost for each coefficient position
void compute_conv_and_cost(
    ap_int<16> basic_memory,
    ap_int<16> coeff_memory,
    ap_int<16> patch_memory,
 
   ap_int<24> delta_memory,
    ap_int<32> grad_memory,
    ap_int<45> &cost
) {
    for(int i = 0; i < (coeff_depth - basic_depth + 1); ++i) {
        ap_int<16> is = i + 4000*coeff_rank;
        int conv_ones = 0;
        for(int j = 0; j < basic_depth ; ++j){
            conv_ones += basic_memory[j] * coeff_memory[is + basic_depth - 1];
        }
        ap_int<24> deltaValue = patch_memory[i] - conv_ones;
        delta_memory[i] = deltaValue;
        cost += deltaValue * deltaValue + lambda * hls::abs(coeff_memory[is]);
    }
}
"""
    algo_name = "bfgs"
    func_description = "bfgs"
    # stage_opt_list = ["pragma HLS ARRAY_PARTITION", "pragma HLS DEPENDENCE"]
    # apply_opt(stage_code, stage_opt_list, algo_name, func_description)
    run_stage_code_opt(stage_code)
    # connection_test()
    # connection_test()

# """
# // Stage 2: Process edges from the stream and update depths
# static void edge_processing_stage(
#     char *depth,
#     const int *ciao,
#     hls::stream<edge_stream_t> &edge_stream,
#     const char level_plus1
# ) {

#     int ngb_vidx;
#     char ngb_depth;
#     edge_stream_t edge_to_process;

#     while (!edge_stream.empty()) {
#         edge_to_process = edge_stream.read();
#         for (int j = edge_to_process.start; j < edge_to_process.end; j++) {
#             ngb_vidx = ciao[j];
#             ngb_depth = depth[ngb_vidx];

#             if (ngb_depth == -1) {
#                 depth[ngb_vidx] = level_plus1;
#             }
#         }
#     }
# }
# """