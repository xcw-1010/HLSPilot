# HLSPilot

HLSPilot is the first automatic HLS code generation and optimization framework from sequential C/C++ code using LLM. 

This framework investigates the use of LLM for HLS design strategy learning and tool learning, and build a complete hardware acceleration workflow ranging from runtime profiling, kernel identification, automatic HLS code generation, design space exploration, and HW/SW co-design on a hybrid CPU-FPGA computing architecture.

## Usage

0. Place your code under benchmark directory

1. Run Code Analysis：

   ```shell
   python3 src/hw_sw_partition/auto_analysis.py
   ```

2. Task pipeline：

   ```shell
   python3 src/task_pipeline/task_pipeline.py
   ```

3. Task optimization：

   ```shell
   python3 src/task_opt/task_opt.py
   ```

4. DSE：

   ```shell
   cd src/auto_dse
   python3 aoto_dse.py
   ./exec.sh run APP_NAME .cpp
   ```

   

