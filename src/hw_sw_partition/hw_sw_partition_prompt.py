SYSTEM_PROMPT = \
"""
You are an FPGA engineer and you are designing an accelerator using HLS(high-level-synthesis).
Here is a software code for {ALGO_NAME}. Your goal is to optimize this code to make it work more efficiently on CPU-FPGA hybrid platform.
"""

CODE_ANALYSIS_PROMPT = \
"""
The first step is to partition the software and hardware of the code. At this stage, you need to perform dynamic and static analysis on the code, identify performance bottlenecks in hardware acceleration, and place appropriate functions on FPGA for acceleration.
The following is the content of the code and the profiling report obtained using gprof:
----------------------------------------------------
code content: 
{CODE_CONTENT}
----------------------------------------------------
profiling report:
{REPORT_CONTENT}
Please extract the following performance indicators for each function based on the code content and report:
Execution time, computational intensity, data intensity, parallelism
Please note that some indicators (such as parallelism, computational intensity, and data intensity) may be difficult to present numerically. For these indicators, please use a score between 1 and 10 to evaluate them. The higher the score, the higher the degree.
Please return the final result in JSON format.
----------------------------------------------------
"""
