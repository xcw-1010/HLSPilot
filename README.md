# HLSPilot

HLSPilot is the first automatic HLS code generation and optimization framework from sequential C/C++ code using LLM. 

This framework investigates the use of LLM for HLS design strategy learning and tool learning, and build a complete hardware acceleration workflow ranging from runtime profiling, kernel identification, automatic HLS code generation, design space exploration, and HW/SW co-design on a hybrid CPU-FPGA computing architecture.

## Prerequisites

This project was tested on Xilinx Alveo U280 and Vitis HLS 2019.1 suite. The following python libraries are required: 
* openai (v1.33.0)
* langchain (v0.2.3)

## Usage

0. Place your code under benchmark directory

1. Run Code Analysis: This step will call the gprof tool to profile the code and extract performance bottlenecks, thereby helping to complete the HW-SW partition.

   ```shell
   python3 src/hw_sw_partition/auto_analysis.py
   ```

2. Task pipeline: This step will split the kernel into multiple subtasks, allowing for pipeline execution between subtasks and improving program parallelism.

   ```shell
   python3 src/task_pipeline/task_pipeline.py
   ```

3. Task optimization: This step will optimize the subtask code by retrieving suitable pragma from the optimization strategy knowledge base and applying it to the code.

   ```shell
   python3 src/task_opt/task_opt.py
   ```

4. DSE: This step will call the DSE tool to complete the parameter tuning of pragma

   ```shell
   cd src/auto_dse
   python3 aoto_dse.py
   ./exec.sh run APP_NAME .cpp
   ```

   

