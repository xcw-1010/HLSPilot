BASELINE_PROMPT = \
"""
You are an FPGA engineer and you are designing a graph processing accelerator using HLS(high-level-synthesis).
Here is a kernel code for BFS, which serially implements the BFS algorithm. Please optimize this code to make it work more efficiently.

static void bfs_kernel(
    char        *depth, 
    const int   *rpao, 
    const int   *ciao, 
    int         *frontier_size, 
    int         vertex_num, 
    const char  level, 
    const char  level_plus1
) {
    char d;
    int start, end;
    int ngb_vidx;
    char ngb_depth;
    int counter = 0;
    for (int i = 0; i < vertex_num; i++) {
        d = depth[i];
        if (d == level) {
            counter++;
            start = rpao[i];
            end = rpao[i + 1];
            for (int j = start; j < end; j++) {
                ngb_vidx = ciao[j];
                ngb_depth = depth[ngb_vidx];
                if (ngb_depth == -1) {
                    depth[ngb_vidx] = level_plus1;
                }
            }
        }
    }
    *frontier_size = counter;
}

extern "C" {
    void bfs(
        char        *depth, 
        const int   *rpao, 
        const int   *ciao, 
        int         *frontier_size, 
        const int   vertex_num, 
        const char  level
    ) {
#pragma HLS INTERFACE m_axi port=depth offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=rpao offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=ciao offset=slave bundle=gmem2
#pragma HLS INTERFACE m_axi port=frontier_size offset=slave bundle=gmem3

#pragma HLS INTERFACE s_axilite port=vertex_num bundle=control
#pragma HLS INTERFACE s_axilite port=level bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

        char level_plus1 = level + 1;
        bfs_kernel(depth, rpao, ciao, frontier_size, vertex_num, level, level_plus1);
    }
}
"""

# task pipeline for bfs
PIPELINE_PROMPT_1 = \
"""
You are an FPGA engineer and you are designing a graph processing accelerator using HLS(high-level-synthesis).
Here is a kernel code for BFS, which serially implements the BFS algorithm.

Dividing the graph algorithm into multiple stages enables Vivado HLS to generate an implementation method that allows different stages of the algorithm to run on different datasets. This optimization method uses dataflow instructions, called task pipelining, which is very common and suitable for various hardware optimization methods.

Please optimize this code to make it work more efficiently according to the task pipelining method. 

static void bfs_kernel(
    char        *depth, 
    const int   *rpao, 
    const int   *ciao, 
    int         *frontier_size, 
    int         vertex_num, 
    const char  level, 
    const char  level_plus1
) {
    char d;
    int start, end;
    int ngb_vidx;
    char ngb_depth;
    int counter = 0;
    for (int i = 0; i < vertex_num; i++) {
        d = depth[i];
        if (d == level) {
            counter++;
            start = rpao[i];
            end = rpao[i + 1];
            for (int j = start; j < end; j++) {
                ngb_vidx = ciao[j];
                ngb_depth = depth[ngb_vidx];
                if (ngb_depth == -1) {
                    depth[ngb_vidx] = level_plus1;
                }
            }
        }
    }
    *frontier_size = counter;
}

extern "C" {
    void bfs(
        char        *depth, 
        const int   *rpao, 
        const int   *ciao, 
        int         *frontier_size, 
        const int   vertex_num, 
        const char  level
    ) {
#pragma HLS INTERFACE m_axi port=depth offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=rpao offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=ciao offset=slave bundle=gmem2
#pragma HLS INTERFACE m_axi port=frontier_size offset=slave bundle=gmem3

#pragma HLS INTERFACE s_axilite port=vertex_num bundle=control
#pragma HLS INTERFACE s_axilite port=level bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

        char level_plus1 = level + 1;
        bfs_kernel(depth, rpao, ciao, frontier_size, vertex_num, level, level_plus1);
    }
}
"""

# task pipeline for pagerank
PIPELINE_PROMPT_2 = \
"""
You are an FPGA engineer and you are designing a graph processing accelerator using HLS(high-level-synthesis).
Here is a kernel code for PageRank, which serially implements the PageRank algorithm.

Dividing the graph algorithm into multiple stages enables Vivado HLS to generate an implementation method that allows different stages of the algorithm to run on different datasets. This optimization method uses dataflow instructions, called task pipelining, which is very common and suitable for various hardware optimization methods.

Please optimize this code to make it work more efficiently according to the task pipelining method. 

static void pagerank_kernel(
    const int *rpao, 
    const int *ciao, 
    float *pr, 
    const int vertex_num, 
    const float damping_factor, 
    const int max_iterations
) {
    initialization:
    for (int i = 0; i < vertex_num; i++) {
        pr[i] = 1.0 / vertex_num;
    }

    for (int iter = 0; iter < max_iterations; iter++) {
        float new_pr[vertex_num];

        for (int i = 0; i < vertex_num; i++) {
            int start = rpao[i];
            int end = rpao[i + 1];
            
            for (int j = start; j < end; j++) {
                int ngb_idx = ciao[j];
                new_pr[ngb_idx] += pr[i] / (end - start);
            }
        }

        for (int i = 0; i < vertex_num; i++) {
            new_pr[i] = (1.0 - damping_factor) / vertex_num + damping_factor * new_pr[i];
        }
    }

}

extern "C" {
    void pagerank(
        const int *rpao, 
        const int *ciao, 
        float *pr, 
        const int vertex_num, 
        const float damping_factor, 
        const int max_iterations
    ) {

#pragma HLS INTERFACE m_axi port=rpao offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=ciao offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=pr offset=slave bundle=gmem2

#pragma HLS INTERFACE s_axilite port=vertex_num bundle=control
#pragma HLS INTERFACE s_axilite port=damping_factor bundle=control
#pragma HLS INTERFACE s_axilite port=max_iterations bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

        pagerank_kernel(rpao, ciao, pr, vertex_num, damping_factor, max_iterations);
    }
}
"""

# task pipeline for bfs (with hint: read-compute-write pattern)
PIPELINE_PROMPT_3 = \
"""
You are an FPGA engineer and you are designing a graph processing accelerator using HLS(high-level-synthesis).
Here is a kernel code for BFS, which serially implements the BFS algorithm.

Dividing the graph algorithm into multiple stages enables Vivado HLS to generate an implementation method that allows different stages of the algorithm to run on different datasets. This optimization method uses dataflow instructions, called task pipelining, which is very common and suitable for various hardware optimization methods.

Please optimize this code to make it work more efficiently according to the task pipelining method. 

static void bfs_kernel(
    char        *depth, 
    const int   *rpao, 
    const int   *ciao, 
    int         *frontier_size, 
    int         vertex_num, 
    const char  level, 
    const char  level_plus1
) {
    char d;
    int start, end;
    int ngb_vidx;
    char ngb_depth;
    int counter = 0;
    for (int i = 0; i < vertex_num; i++) {
        d = depth[i];
        if (d == level) {
            counter++;
            start = rpao[i];
            end = rpao[i + 1];
            for (int j = start; j < end; j++) {
                ngb_vidx = ciao[j];
                ngb_depth = depth[ngb_vidx];
                if (ngb_depth == -1) {
                    depth[ngb_vidx] = level_plus1;
                }
            }
        }
    }
    *frontier_size = counter;
}

extern "C" {
    void bfs(
        char        *depth, 
        const int   *rpao, 
        const int   *ciao, 
        int         *frontier_size, 
        const int   vertex_num, 
        const char  level
    ) {
#pragma HLS INTERFACE m_axi port=depth offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=rpao offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=ciao offset=slave bundle=gmem2
#pragma HLS INTERFACE m_axi port=frontier_size offset=slave bundle=gmem3

#pragma HLS INTERFACE s_axilite port=vertex_num bundle=control
#pragma HLS INTERFACE s_axilite port=level bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

        char level_plus1 = level + 1;
        bfs_kernel(depth, rpao, ciao, frontier_size, vertex_num, level, level_plus1);
    }
}

You can consider partitioning the code into a Load-Compute-Store pattern:
1.read_dataflow: Read the data.
2.compute_dataflow: Process the data.
3.write_dataflow: Write the output to the main memory.
"""

TEST_PROMPT = \
f"""
Write a C++ code to calculate fibonacci number. Place the code in ``` ```.
"""

SYNTH_RPT_PROMPT = \
f"""
The following is a vivado HLS(high-level-synthesis) report for an FPGA-based BFS accelerator. Please help me analysis the report and indicate how to optimize it.

================================================================
== Vivado HLS Report for 'bfs'
================================================================
* Date:           Mon Dec 11 17:13:59 2023

* Version:        2019.2.1 (Build 2724168 on Thu Dec 05 05:19:09 MST 2019)
* Project:        bfs
* Solution:       solution
* Product family: virtexuplus
* Target device:  xcu280-fsvh2892-2L-e


================================================================
== Performance Estimates
================================================================
+ Timing: 
    * Summary: 
    +--------+---------+----------+------------+
    |  Clock |  Target | Estimated| Uncertainty|
    +--------+---------+----------+------------+
    |ap_clk  | 3.33 ns | 2.433 ns |   0.90 ns  |
    +--------+---------+----------+------------+

+ Latency: 
    * Summary: 
    +---------+---------+----------+----------+-----+-----+---------+
    |  Latency (cycles) |  Latency (absolute) |  Interval | Pipeline|
    |   min   |   max   |    min   |    max   | min | max |   Type  |
    +---------+---------+----------+----------+-----+-----+---------+
    |        ?|        ?|         ?|         ?|    ?|    ?|   none  |
    +---------+---------+----------+----------+-----+-----+---------+

    + Detail: 
        * Instance: 
        +-----------------------+------------+---------+---------+----------+----------+-----+-----+---------+
        |                       |            |  Latency (cycles) |  Latency (absolute) |  Interval | Pipeline|
        |        Instance       |   Module   |   min   |   max   |    min   |    max   | min | max |   Type  |
        +-----------------------+------------+---------+---------+----------+----------+-----+-----+---------+
        |grp_bfs_kernel_fu_118  |bfs_kernel  |        ?|        ?|         ?|         ?|    ?|    ?|   none  |
        +-----------------------+------------+---------+---------+----------+----------+-----+-----+---------+

        * Loop: 
        N/A



================================================================
== Utilization Estimates
================================================================
* Summary: 
+---------------------+---------+-------+---------+---------+-----+
|         Name        | BRAM_18K| DSP48E|    FF   |   LUT   | URAM|
+---------------------+---------+-------+---------+---------+-----+
|DSP                  |        -|      -|        -|        -|    -|
|Expression           |        -|      -|        0|       14|    -|
|FIFO                 |        -|      -|        -|        -|    -|
|Instance             |        8|      -|     3207|     3837|    -|
|Memory               |        -|      -|        -|        -|    -|
|Multiplexer          |        -|      -|        -|      123|    -|
|Register             |        -|      -|      307|        -|    -|
+---------------------+---------+-------+---------+---------+-----+
|Total                |        8|      0|     3514|     3974|    0|
+---------------------+---------+-------+---------+---------+-----+
|Available SLR        |     1344|   3008|   869120|   434560|  320|
+---------------------+---------+-------+---------+---------+-----+
|Utilization SLR (%)  |    ~0   |      0|    ~0   |    ~0   |    0|
+---------------------+---------+-------+---------+---------+-----+
|Available            |     4032|   9024|  2607360|  1303680|  960|
+---------------------+---------+-------+---------+---------+-----+
|Utilization (%)      |    ~0   |      0|    ~0   |    ~0   |    0|
+---------------------+---------+-------+---------+---------+-----+
"""

PROFILE_PROMPT = \
f"""
The following is a vivado HLS(high-level-synthesis) Profile report for an FPGA-based BFS accelerator. Please help me analysis the report and indicate how to optimize it.

Profile Summary													
Generated on: 2023-12-12 15:10:38													
Msec since Epoch: 1702365038918													
Profiled application: host													
Target platform: 													
Tool version: 2019.2													
XRT build version: 2.3.1301													
Build version branch: 2019.2													
Build version hash: 192e706aea53163a04c574f9b3fe9ed76b6ca471													
Build version date: 2019-10-25 03:04:42													
Target devices: xilinx_u280_xdma_201920_1-0													
Flow mode: System Run													
													
OpenCL API Calls													
API Name	Number Of Calls	Total Time (ms)	Minimum Time (ms)	Average Time (ms)	Maximum Time (ms)								
clCreateProgramWithBinary	1	3006.01	3006.01	3006.01	3006.01								
clFinish	7	163.746	0.016429	23.3923	115.999								
clReleaseProgram	1	12.8983	12.8983	12.8983	12.8983								
clEnqueueWriteBuffer	3	1.8449	0.038787	0.614968	1.697								
clEnqueueReadBuffer	7	1.66626	0.206627	0.238038	0.278994								
clCreateKernel	1	1.24543	1.24543	1.24543	1.24543								
clReleaseKernel	1	1.06989	1.06989	1.06989	1.06989								
clEnqueueNDRangeKernel	6	0.927035	0.094393	0.154506	0.207475								
clCreateBuffer	4	0.894804	0.021292	0.223701	0.710949								
clGetEventProfilingInfo	12	0.1673	0.00602	0.0139417	0.044								
clSetKernelArg	11	0.141434	0.005273	0.0128576	0.036363								
clGetExtensionFunctionAddress	2	0.105978	0.023943	0.052989	0.082035								
clGetPlatformInfo	14	0.10386	0.006749	0.00741857	0.009104								
clReleaseEvent	6	0.089966	0.009036	0.0149943	0.02209								
clReleaseMemObject	4	0.064943	0.013299	0.0162357	0.023246								
clCreateContext	1	0.025463	0.025463	0.025463	0.025463								
clReleaseContext	1	0.024075	0.024075	0.024075	0.024075								
clGetExtensionFunctionAddressForPlatform	2	0.022709	0.008322	0.0113545	0.014387								
clReleaseCommandQueue	1	0.020151	0.020151	0.020151	0.020151								
clGetDeviceInfo	2	0.019914	0.009929	0.009957	0.009985								
clBuildProgram	1	0.01488	0.01488	0.01488	0.01488								
clGetDeviceIDs	1	0.014788	0.014788	0.014788	0.014788								
clCreateCommandQueue	1	0.01457	0.01457	0.01457	0.01457								
													
													
Kernel Execution													
Kernel	Number Of Enqueues	Total Time (ms)	Minimum Time (ms)	Average Time (ms)	Maximum Time (ms)								
bfs	6	163.165	4.12169	27.1942	115.978								
													
													
Compute Unit Utilization													
Device	Compute Unit	Kernel	Global Work Size	Local Work Size	Number Of Calls	Dataflow Execution	Max Overlapping Executions	Dataflow Acceleration	Total Time (ms)	Minimum Time (ms)	Average Time (ms)	Maximum Time (ms)	Clock Frequency (MHz)
xilinx_u280_xdma_201920_1-0	bfs_1	bfs	1:01:01	1:01:01	6	No	1	1.000000x	160.806	3.75922	26.801	115.421	280
													
													
Data Transfer: Host to Global Memory													
Context:Number of Devices	Transfer Type	Number Of Buffer Transfers	Transfer Rate (MB/s)	Average Bandwidth Utilization (%)	Average Buffer Size (KB)	Total Time (ms)	Average Time (ms)						
context0:1	READ	7	25.638982	0.267073	2.344	0.639963	0.091423						
context0:1	WRITE	1	6461.844126	67.310876	2179.08	0.337222	0.337222						
													
													
Data Transfer: Kernels to Global Memory													
Device	Compute Unit/Port Name	Kernel Arguments	Memory Resources	Transfer Type	Number Of Transfers	Transfer Rate (MB/s)	Average Bandwidth Utilization (%)	Average Size (KB)	Average Latency (ns)				
xilinx_u280_xdma_201920_1-0	bfs_1/m_axi_gmem0	depth	HBM[0]	READ	620582	22.4669	0.195025	0.004	178.04				
xilinx_u280_xdma_201920_1-0	bfs_1/m_axi_gmem0	depth	HBM[0]	WRITE	12571	12.7273	0.11048	0.001	78.5714				
xilinx_u280_xdma_201920_1-0	bfs_1/m_axi_gmem1	rpao	HBM[0]	READ	25144	40.6122	0.352536	0.004	191.83				
xilinx_u280_xdma_201920_1-0	bfs_1/m_axi_gmem2	ciao	HBM[0]	READ	522278	22.3289	0.193827	0.004	179.14				
xilinx_u280_xdma_201920_1-0	bfs_1/m_axi_gmem3	frontier_size	HBM[0]	WRITE	6	50.9091	0.441919	0.004	78.5714				
													
													
Top Data Transfer: Kernels to Global Memory													
Device	Compute Unit	Number of Transfers	Average Bytes per Transfer	Transfer Efficiency (%)	Total Data Transfer (MB)	Total Write (MB)	Total Read (MB)	Total Transfer Rate (MB/s)					
xilinx_u280_xdma_201920_1-0	bfs_1	1180581	3.96806	0.0968764	4.68461	0.012595	4.67202	22.5749					
													
													
Top Kernel Execution													
Kernel Instance Address	Kernel	Context ID	Command Queue ID	Device	Start Time (ms)	Duration (ms)	Global Work Size	Local Work Size					
26179296	bfs	0	0	xilinx_u280_xdma_201920_1-0	3175.74	115.978	1:01:01	1:01:01					
26179296	bfs	0	0	xilinx_u280_xdma_201920_1-0	3149.86	25.2692	1:01:01	1:01:01					
26179296	bfs	0	0	xilinx_u280_xdma_201920_1-0	3292.31	9.46004	1:01:01	1:01:01					
26179296	bfs	0	0	xilinx_u280_xdma_201920_1-0	3145.13	4.20816	1:01:01	1:01:01					
26179296	bfs	0	0	xilinx_u280_xdma_201920_1-0	3307.29	4.12813	1:01:01	1:01:01					
26179296	bfs	0	0	xilinx_u280_xdma_201920_1-0	3302.44	4.12169	1:01:01	1:01:01					
													
													
Top Memory Writes: Host to Global Memory													
Buffer Address	Context ID	Command Queue ID	Start Time (ms)	Duration (ms)	Buffer Size (KB)	Writing Rate(MB/s)							
2166784	0	0	3144.7	0.337222	2179.08	6461.844126							
													
													
Top Memory Reads: Host to Global Memory													
Buffer Address	Context ID	Command Queue ID	Start Time (ms)	Duration (ms)	Buffer Size (KB)	Reading Rate(MB/s)							
2183168	0	0	3149.55	0.135815	0.004	0.029452							
2183168	0	0	3175.37	0.11419	0.004	0.035029							
2183168	0	0	3302.08	0.087409	0.004	0.045762							
2166784	0	0	3312.11	0.083004	16.384	197.388078							
2183168	0	0	3311.84	0.077426	0.004	0.051662							
2183168	0	0	3306.94	0.076695	0.004	0.052155							
2183168	0	0	3291.96	0.065424	0.004	0.06114							
													
													
Guidance Parameters													
Parameter	Element	Value											
DEVICE_EXEC_TIME	xilinx_u280_xdma_201920_1-0	166.289828											
CU_CALLS	xilinx_u280_xdma_201920_1-0|bfs_1	6											
MEMORY_BIT_WIDTH	xilinx_u280_xdma_201920_1-0	512											
MIGRATE_MEM	host	0											
MEMORY_USAGE	HBM[0]	4											
PLRAM_DEVICE	all	1											
HBM_DEVICE	all	1											
KDMA_DEVICE	all	0											
P2P_DEVICE	all	0											
P2P_HOST_TRANSFERS	host	0											
PORT_BIT_WIDTH	bfs_1/m_axi_gmem0	32											
PORT_BIT_WIDTH	bfs_1/m_axi_gmem1	32											
PORT_BIT_WIDTH	bfs_1/m_axi_gmem2	32											
PORT_BIT_WIDTH	bfs_1/m_axi_gmem3	32											
KERNEL_COUNT	bfs	1											
OBJECTS_RELEASED	all	1											
TRACE_MEMORY	all	FIFO											
CU_CONTEXT_EN	all	0											

"""

OPT_CHOOSE_PROMPT_TEST = \
"""
In HLS(high-level-synthesis), code optimization can be achieved by adding various types of compilation directive (pragmas). Different pragmas are suitable for different scenarios and cannot be applied arbitrarily. The following are some function introductions and applicable scenarios of pragmas:

pragma HLS allocation

Function Overview:
pragma HLS allocation is a compilation directive to restrict the allocation of hardware resources within implemented kernels. It allows users to specify the number of instances to be limited in functions, loops, or code regions, thereby controlling resource usage in the generated hardware design.

Application Scenes:
- When there is a need to limit the number of hardware resource instances in specific functions, loops, or code regions for optimizing either resource utilization or performance.
- In scenarios where there are multiple instances in the design, controlling resource usage by limiting the instance count for hardware-level optimization.
-----------------------
pragma HLS resource

Function Overview:
pragma HLS resource is one of the compilation directives to specify particular library resources (cores) for implementing variables (arrays, arithmetic operations, or function parameters) in RTL. Users can control which core to use to implement operations in the code using this pragma.

Application Scenes:
- When there is a need to explicitly specify a particular core from the library for implementing a specific operation. 
- In scenarios where multiple cores are available for implementing the same functionality, choosing the appropriate core through this pragma to meet performance or resource optimization requirements.
- Controlling whether an array is implemented as a single-port RAM or dual-port RAM.
-----------------------
pragma HLS inline

Function Overview:
pragma HLS inline is a compilation directive to control the inlining behavior of functions. Inlining removes functions 
as separate entities in the hierarchy by inserting the code of the called function directly at the call site, eliminating the need for a separate hierarchy. This directive allows users to selectively enable or disable inlining for functions and specify the scope and recursion level of inlining.

Application Scenes:
- When eliminating the hierarchy of function calls in RTL generation to improve code execution efficiency and sharing optimization.
- In scenarios where control over the scope and recursion level of inlined functions is needed to meet optimization requirements for performance or resource utilization.
-----------------------
pragma HLS function_instantiate

Overview:
pragma HLS function_instantiate directive is a compilation directive to optimize function instantiation, aiming to improve performance and reduce resource utilization. This directive allows the creation of unique hardware descriptions for each instance of a function, enabling targeted local optimizations. By default, all instances of the same function share a hardware implementation, but using this directive facilitates local optimizations for each instance.

Application Scenes:
- It is applicable when the same function has different constant parameter values in various instance calls. This directive helps generate independent hardware implementations for each instance, optimizing performance.
- When there is a need to reduce the complexity of control logic while improving latency and throughput, using this directive effectively utilizes hardware resources.
-----------------------
pragma HLS stream

Function Overview:
pragma HLS stream is a compilation directive to specify the implementation approach for array variables. By default, arrays are implemented as RAM, but this directive allows the choice of implementing arrays as a streaming interface using FIFOs instead of RAM, offering a more efficient communication mechanism.

Application Scenes:
- It is applicable when dealing with data stored in arrays that is used or generated in a sequential manner, as using streaming data instead of RAM can enhance communication efficiency.
- It can be used when there is a need to reduce the depth of the FIFO in the data flow channel to decrease resource utilization.
-----------------------
pragma HLS pipeline

Function Overview:
pragma HLS pipeline is a compilation directive to reduce the initiation interval of functions or loops, thereby improving performance through concurrent execution of operations. It allows the pipelining of operations in functions or loops to process new inputs every N clock cycles, where N is the initiation interval (II) of the loop or function. The default II is 1, meaning a new input is processed every clock cycle.

Application Scenes:
- It is suitable for scenarios where reducing the initiation interval of functions or loops is desired to enhance concurrent performance.
- It is applicable for optimizing performance by pipelining loops to enable concurrent execution of operations.        
-----------------------
pragma HLS Occurrence

Function Overview:
pragma HLS occurrence is used to specify that the code within a particular region has a lower execution frequency compared to the enclosing loop or function. This pragma allows for more efficient pipelining of code with lower execution frequency, potentially enabling sharing in the top-level pipeline.

Application Scenes:
- It is suitable for specific regions within loops or functions where the execution frequency is lower than that of the enclosing loop or function.
-----------------------
pragma HLS unroll

Function Overview:
pragma HLS unroll is a compilation directive to unroll loops, creating multiple independent operations instead of a single operation set. The UNROLL compilation directive transforms loops by creating multiple copies of the loop body in the RTL design, allowing parallel execution of some or all loop iterations.

Application Scenes:
- When increased loop parallelism is desired to enhance performance and throughput.
- When optimizing hardware implementation to execute multiple loop iterations in the same clock cycle.
-----------------------
pragma HLS dependence

Function Overview:
pragma HLS dependence is a compilation directive used to control loop dependencies. This directive provides additional 
information to overcome loop carry dependencies, allowing for loop pipelining or pipelining with lower intervals to optimize hardware performance.

Application Scenes:
- It is used when automatic dependency detection by Vivado HLS is inaccurate or overly conservative.
- It is employed in cases where there are complex dependencies within or between different loop iterations, and precise control is needed.
-----------------------
pragma HLS loop_flatten

Function Overview:
The pragma HLS loop_flatten allows the flattening of nested loops into a single loop hierarchy to improve latency. Flattening nested loops can reduce clock cycles, enabling greater optimization of loop body logic, particularly in RTL (Register-Transfer Level) implementations.

Application Scenes:
- Applicable to perfect and imperfect loops where only the innermost loop contains loop body content.
- No specified logic between loop statements.
- All loop boundaries are constants.
- For imperfect loops, the outermost loop boundary can be a variable.
-----------------------
pragma HLS loop_merge

Function Overview:
The pragma HLS loop_merge is used to merge consecutive loops into a single loop, reducing overall latency, promoting sharing, and improving logic optimization. Loop merging aims to decrease the number of clock cycles needed for transitions between loop body implementations in RTL (Register-Transfer Level) and allows for parallel implementation of loops.  

Application Scenes:
- Applicable to consecutive loops where loop boundaries have the same values or share the maximum constant value.      
- Suitable for loops where it can be ensured that the loop body code does not have one-sided effects and produces the same results upon multiple executions.
-----------------------
pragma HLS loop_tripcount

Function Overview:
pragma HLS loop_tripcount is used to manually specify the total number of iterations for a loop. It aids the tool in analysis without affecting the synthesis results. This directive allows users to specify the minimum, maximum, and average iteration counts for a loop, enabling synthesis analysis and optimization in cases where the loop iteration count is 
unknown or cannot be determined dynamically.

Application Scenes:
- When Vivado HLS cannot determine the iteration count of a loop, especially for variables dependent on input parameters or dynamically computed operations.
- In situations requiring manual specification of loop iteration counts for synthesis analysis and optimization.       
-----------------------
pragma HLS array_map

Function Overview:
pragma HLS array_map is used to combine multiple smaller arrays into a larger array, optimizing the utilization of block RAM resources. It supports two mapping methods: horizontal mapping, where original array elements are connected to create a new array, and vertical mapping, where array fields are connected to form a new array. The main purpose of this 
compilation directive is to more efficiently utilize block RAM units in FPGA physically.

Application Scenes:
- When there are multiple smaller arrays.
- When the use of block RAM needs to be optimized in the FPGA design, especially if the target hardware supports block 
RAM or UltraRAM.
-----------------------
pragma HLS array_partition

Function Overview:
This pragma is used to partition arrays, dividing them into smaller arrays or individual elements. The partitioning results in generating multiple small memories or registers at the RTL (Register-Transfer Level) instead of a single large 
memory. This effectively increases the number of read and write ports, potentially enhancing the design's throughput.  

Application Scenes:
- When there is a need to increase the number of storage read and write ports to enhance parallelism and throughput.   
- Optimizing multi-dimensional arrays in HLS designs, especially in array operations within processors.
-----------------------
pragma HLS array_reshape

Function Overview:
The array_reshape pragma is used to reshape arrays by combining the effects of array partitioning and vertical array mapping. It allows breaking down arrays into smaller ones while connecting array elements by increasing the bit width to 
enhance parallel access and enable access to more data within a single clock cycle. This directive creates a new array 
with fewer elements but a larger bit width.

Application Scenes:
- When optimizing parallel access to arrays for improved performance.
- In cases where reducing the number of block RAMs is needed while maintaining efficient access to arrays.
- When reshaping arrays to meet specific hardware constraints.
-----------------------
pragma HLS data_pack

Function Overview:
pragma HLS data_pack is a compilation directive to pack data fields of a structure into a scalar with a wider bit width. This helps reduce the memory required for variables while allowing simultaneous read and write access to all members 
of the structure. It is used in hardware design to optimize memory access and data storage.

Application Scenes:
- Optimize the memory layout of structures to reduce storage space requirements.
- Improve memory access efficiency, allowing simultaneous read and write access to all members of a structure.
- In hardware design, especially in FPGA design, optimize data storage and access.
-----------------------
The following code is one stage of the algorithm. Please determine which kind of optimizations can be applied to this stage. You can choose some optimization options that are most suitable for applying to this stage of code from the following optimization options

// Stage 2: Process edges from the stream and update depths
static void edge_processing_stage(
    char *depth,
    const int *ciao,
    hls::stream<edge_stream_t> &edge_stream,
    const char level_plus1
) {
#pragma HLS INLINE off

    int ngb_vidx;
    char ngb_depth;
    edge_stream_t edge_to_process;

    while (!edge_stream.empty()) {
#pragma HLS PIPELINE II=1
        edge_to_process = edge_stream.read();
        for (int j = edge_to_process.start; j < edge_to_process.end; j++) {
            ngb_vidx = ciao[j];
            ngb_depth = depth[ngb_vidx];

            if (ngb_depth == -1) {
                depth[ngb_vidx] = level_plus1;
            }
        }
    }
}

Note that not all optimization options are suitable for this stage.
You only need to select the suitable optimization options, without providing the optimized code.
Please return the answer in the following format: [option_1, option_2, ..., option_n]
If the code no longer needs optimization, you can return null.
"""

# choose suitable opt pragma for stage2 of convolution
OPT_CHOOSE_PROMPT_TEST2 = \
"""
In HLS(high-level-synthesis), code optimization can be achieved by adding various types of compilation directive (pragmas). Different pragmas are suitable for different scenarios and cannot be applied arbitrarily. The following are some function introductions and applicable scenarios of pragmas:

pragma HLS allocation

Function Overview:
pragma HLS allocation is a compilation directive to restrict the allocation of hardware resources within implemented kernels. It allows users to specify the number of instances to be limited in functions, loops, or code regions, thereby controlling resource usage in the generated hardware design.

Application Scenes:
- When there is a need to limit the number of hardware resource instances in specific functions, loops, or code regions for optimizing either resource utilization or performance.
- In scenarios where there are multiple instances in the design, controlling resource usage by limiting the instance count for hardware-level optimization.
-----------------------
pragma HLS resource

Function Overview:
pragma HLS resource is one of the compilation directives to specify particular library resources (cores) for implementing variables (arrays, arithmetic operations, or function parameters) in RTL. Users can control which core to use to implement operations in the code using this pragma.

Application Scenes:
- When there is a need to explicitly specify a particular core from the library for implementing a specific operation. 
- In scenarios where multiple cores are available for implementing the same functionality, choosing the appropriate core through this pragma to meet performance or resource optimization requirements.
- Controlling whether an array is implemented as a single-port RAM or dual-port RAM.
-----------------------
pragma HLS inline

Function Overview:
pragma HLS inline is a compilation directive to control the inlining behavior of functions. Inlining removes functions 
as separate entities in the hierarchy by inserting the code of the called function directly at the call site, eliminating the need for a separate hierarchy. This directive allows users to selectively enable or disable inlining for functions and specify the scope and recursion level of inlining.

Application Scenes:
- When eliminating the hierarchy of function calls in RTL generation to improve code execution efficiency and sharing optimization.
- In scenarios where control over the scope and recursion level of inlined functions is needed to meet optimization requirements for performance or resource utilization.
-----------------------
pragma HLS function_instantiate

Overview:
pragma HLS function_instantiate directive is a compilation directive to optimize function instantiation, aiming to improve performance and reduce resource utilization. This directive allows the creation of unique hardware descriptions for each instance of a function, enabling targeted local optimizations. By default, all instances of the same function share a hardware implementation, but using this directive facilitates local optimizations for each instance.

Application Scenes:
- It is applicable when the same function has different constant parameter values in various instance calls. This directive helps generate independent hardware implementations for each instance, optimizing performance.
- When there is a need to reduce the complexity of control logic while improving latency and throughput, using this directive effectively utilizes hardware resources.
-----------------------
pragma HLS stream

Function Overview:
pragma HLS stream is a compilation directive to specify the implementation approach for array variables. By default, arrays are implemented as RAM, but this directive allows the choice of implementing arrays as a streaming interface using FIFOs instead of RAM, offering a more efficient communication mechanism.

Application Scenes:
- It is applicable when dealing with data stored in arrays that is used or generated in a sequential manner, as using streaming data instead of RAM can enhance communication efficiency.
- It can be used when there is a need to reduce the depth of the FIFO in the data flow channel to decrease resource utilization.
-----------------------
pragma HLS pipeline

Function Overview:
pragma HLS pipeline is a compilation directive to reduce the initiation interval of functions or loops, thereby improving performance through concurrent execution of operations. It allows the pipelining of operations in functions or loops to process new inputs every N clock cycles, where N is the initiation interval (II) of the loop or function. The default II is 1, meaning a new input is processed every clock cycle.

Application Scenes:
- It is suitable for scenarios where reducing the initiation interval of functions or loops is desired to enhance concurrent performance.
- It is applicable for optimizing performance by pipelining loops to enable concurrent execution of operations.        
-----------------------
pragma HLS Occurrence

Function Overview:
pragma HLS occurrence is used to specify that the code within a particular region has a lower execution frequency compared to the enclosing loop or function. This pragma allows for more efficient pipelining of code with lower execution frequency, potentially enabling sharing in the top-level pipeline.

Application Scenes:
- It is suitable for specific regions within loops or functions where the execution frequency is lower than that of the enclosing loop or function.
-----------------------
pragma HLS unroll

Function Overview:
pragma HLS unroll is a compilation directive to unroll loops, creating multiple independent operations instead of a single operation set. The UNROLL compilation directive transforms loops by creating multiple copies of the loop body in the RTL design, allowing parallel execution of some or all loop iterations.

Application Scenes:
- When increased loop parallelism is desired to enhance performance and throughput.
- When optimizing hardware implementation to execute multiple loop iterations in the same clock cycle.
-----------------------
pragma HLS dependence

Function Overview:
pragma HLS dependence is a compilation directive used to control loop dependencies. This directive provides additional 
information to overcome loop carry dependencies, allowing for loop pipelining or pipelining with lower intervals to optimize hardware performance.

Application Scenes:
- It is used when automatic dependency detection by Vivado HLS is inaccurate or overly conservative.
- It is employed in cases where there are complex dependencies within or between different loop iterations, and precise control is needed.
-----------------------
pragma HLS loop_flatten

Function Overview:
The pragma HLS loop_flatten allows the flattening of nested loops into a single loop hierarchy to improve latency. Flattening nested loops can reduce clock cycles, enabling greater optimization of loop body logic, particularly in RTL (Register-Transfer Level) implementations.

Application Scenes:
- Applicable to perfect and imperfect loops where only the innermost loop contains loop body content.
- No specified logic between loop statements.
- All loop boundaries are constants.
- For imperfect loops, the outermost loop boundary can be a variable.
-----------------------
pragma HLS loop_merge

Function Overview:
The pragma HLS loop_merge is used to merge consecutive loops into a single loop, reducing overall latency, promoting sharing, and improving logic optimization. Loop merging aims to decrease the number of clock cycles needed for transitions between loop body implementations in RTL (Register-Transfer Level) and allows for parallel implementation of loops.  

Application Scenes:
- Applicable to consecutive loops where loop boundaries have the same values or share the maximum constant value.      
- Suitable for loops where it can be ensured that the loop body code does not have one-sided effects and produces the same results upon multiple executions.
-----------------------
pragma HLS loop_tripcount

Function Overview:
pragma HLS loop_tripcount is used to manually specify the total number of iterations for a loop. It aids the tool in analysis without affecting the synthesis results. This directive allows users to specify the minimum, maximum, and average iteration counts for a loop, enabling synthesis analysis and optimization in cases where the loop iteration count is 
unknown or cannot be determined dynamically.

Application Scenes:
- When Vivado HLS cannot determine the iteration count of a loop, especially for variables dependent on input parameters or dynamically computed operations.
- In situations requiring manual specification of loop iteration counts for synthesis analysis and optimization.       
-----------------------
pragma HLS array_map

Function Overview:
pragma HLS array_map is used to combine multiple smaller arrays into a larger array, optimizing the utilization of block RAM resources. It supports two mapping methods: horizontal mapping, where original array elements are connected to create a new array, and vertical mapping, where array fields are connected to form a new array. The main purpose of this 
compilation directive is to more efficiently utilize block RAM units in FPGA physically.

Application Scenes:
- When there are multiple smaller arrays.
- When the use of block RAM needs to be optimized in the FPGA design, especially if the target hardware supports block 
RAM or UltraRAM.
-----------------------
pragma HLS array_partition

Function Overview:
This pragma is used to partition arrays, dividing them into smaller arrays or individual elements. The partitioning results in generating multiple small memories or registers at the RTL (Register-Transfer Level) instead of a single large 
memory. This effectively increases the number of read and write ports, potentially enhancing the design's throughput.  

Application Scenes:
- When there is a need to increase the number of storage read and write ports to enhance parallelism and throughput.   
- Optimizing multi-dimensional arrays in HLS designs, especially in array operations within processors.
-----------------------
pragma HLS array_reshape

Function Overview:
The array_reshape pragma is used to reshape arrays by combining the effects of array partitioning and vertical array mapping. It allows breaking down arrays into smaller ones while connecting array elements by increasing the bit width to 
enhance parallel access and enable access to more data within a single clock cycle. This directive creates a new array 
with fewer elements but a larger bit width.

Application Scenes:
- When optimizing parallel access to arrays for improved performance.
- In cases where reducing the number of block RAMs is needed while maintaining efficient access to arrays.
- When reshaping arrays to meet specific hardware constraints.
-----------------------
pragma HLS data_pack

Function Overview:
pragma HLS data_pack is a compilation directive to pack data fields of a structure into a scalar with a wider bit width. This helps reduce the memory required for variables while allowing simultaneous read and write access to all members 
of the structure. It is used in hardware design to optimize memory access and data storage.

Application Scenes:
- Optimize the memory layout of structures to reduce storage space requirements.
- Improve memory access efficiency, allowing simultaneous read and write access to all members of a structure.
- In hardware design, especially in FPGA design, optimize data storage and access.
-----------------------
The following code is one stage of the algorithm. Please determine which kind of optimizations can be applied to this stage. You can choose some optimization options that are most suitable for applying to this stage of code from the following optimization options

  void compute_dataflow(hls::stream<RGBPixel>& write_stream, hls::stream<RGBPixel>& read_stream,
                        const float* coefficient, int img_width, int elements, int center) {
      static RGBPixel window_mem[COEFFICIENT_SIZE][MAX_WIDTH];
      static fixed coef[COEFFICIENT_SIZE * COEFFICIENT_SIZE];

      for(int i  = 0; i < COEFFICIENT_SIZE*COEFFICIENT_SIZE; i++) {
          coef[i] = coefficient[i];
      }

      int line_idx = 0;
      while(line_idx < center) {
          for(int i = 0; i < img_width; i++) {
              window_mem[line_idx][i] = zero;
          }
          line_idx++;
      }

      while(line_idx < COEFFICIENT_SIZE - 1) {
          for(int ii = 0; ii < img_width; ii++) {
              read_stream >> window_mem[line_idx][ii];
          }
          line_idx++;
      }

      for(int ii = 0; ii < COEFFICIENT_SIZE; ii++) {
          read_stream >> window_mem[line_idx][ii];
      }

      int top_idx = 0;
      int insert_idx = line_idx;
      int window_line_idx = top_idx;
      int j = 0;
      int insert_column_idx = COEFFICIENT_SIZE;
      while(elements--) {
          fixed sum_r = 0, sum_g=0, sum_b=0;
          for(int m = 0; m < COEFFICIENT_SIZE; ++m) {
              for(int n = 0; n < COEFFICIENT_SIZE; ++n) {
                  int jj = j + n - center;
                  RGBPixel tmp = (jj >= 0 && jj < img_width) ? window_mem[window_line_idx][jj] : zero;
                  fixed coef_tmp = coef[m * COEFFICIENT_SIZE + n] * (jj >= 0 && jj < img_width);
                  sum_r += tmp.r * coef_tmp;
                  sum_g += tmp.g * coef_tmp;
                  sum_b += tmp.b * coef_tmp;
              }
              window_line_idx = ((window_line_idx + 1) == COEFFICIENT_SIZE) ? 0 : window_line_idx + 1;
          }
          window_line_idx = top_idx;
          RGBPixel out = {sum_r.to_int(), sum_g.to_int(), sum_b.to_int(), 0};
          write_stream << out;
          j++;
          if(j >= img_width) {
              j = 0;
              top_idx = ((top_idx + 1) == COEFFICIENT_SIZE) ? 0 : top_idx + 1;
              window_line_idx = top_idx;
          }
          read_stream >> window_mem[insert_idx][insert_column_idx++];
          if (insert_column_idx >= img_width) {
              insert_column_idx = 0;
              insert_idx = ((insert_idx + 1) == COEFFICIENT_SIZE) ? 0 : insert_idx + 1;
          }
      }
  }

Note that not all optimization options are suitable for this stage.
You only need to select the suitable optimization options, without providing the optimized code.
Please return the answer in the following format without any explaination: [option_1, option_2, ..., option_n]
If the code no longer needs optimization, you can return null.
"""

DAG_GRAPH_PROMPT_TEST = \
"""
DAG graph can be used to represent the dataflow of a program. Please help me generate the DAG graph for the following code step by step: 
static void bfs_kernel(
    char        *depth, 
    const int   *rpao, 
    const int   *ciao, 
    int         *frontier_size, 
    int         vertex_num, 
    const char  level, 
    const char  level_plus1
) {
    char d;
    int start, end;
    int ngb_vidx;
    char ngb_depth;
    int counter = 0;
    for (int i = 0; i < vertex_num; i++) {
        d = depth[i];
        if (d == level) {
            counter++;
            start = rpao[i];
            end = rpao[i + 1];
            for (int j = start; j < end; j++) {
                ngb_vidx = ciao[j];
                ngb_depth = depth[ngb_vidx];
                if (ngb_depth == -1) {
                    depth[ngb_vidx] = level_plus1;
                }
            }
        }
    }
    *frontier_size = counter;
}
"""

# ask gpt for the task pipeline advice
TASK_PIPELINE_ADVICE_PROMPT = \
"""
You are an FPGA engineer and you are designing an accelerator using HLS(high-level-synthesis).
Given a software code which serially implements an algorithm. Your goal is to optimize this code to make it work more efficiently on FPGA.
The first step is task pipelining. Dividing the algorithm into multiple stages enables HLS to generate an implementation method that allows different stages of the algorithm to run on different datasets. This optimization method uses dataflow instructions, called task pipelining, which is very common and suitable for various hardware optimization methods.
There are many ways to partition the code. How to partition it to maximize algorithm parallelism as much as possible? You can explain with some examples.
"""

# apply memory opt to bfs stage3
MEMORY_OPT_TEST = \
"""
You are an FPGA engineer and you are designing a graph processing accelerator using HLS(high-level-synthesis).

Memory optimization is a crucial aspect of FPGA design, and it involves managing data storage and access efficiently to enhance the overall performance of an accelerator. 

The following code is one stage of the BFS algorithm. Please help me optimize the memory access of this function.

static void bfs_stage3(
    const int *ciao, 
    hls::stream<int64_dt> &rpao_stream, 
    hls::stream<uint1_dt> &rpao_done_stream, 
    hls::stream<int> &ciao_stream, 
    hls::stream<uint1_dt> &ciao_done_stream
) {
    uint1_dt rpao_empty = 0;
    uint1_dt done_empty = 0;
    uint1_dt done = 0;
    int start, end;
    int64_dt rpitem;

    while ((rpao_empty != 1) || (done != 1)) {
        rpao_empty = rpao_stream.empty();
        done_empty = rpao_done_stream.empty();

        if (rpao_empty != 1) {
            rpitem = rpao_stream.read();
            start = rpitem.range(31, 0);
            end = rpitem.range(63, 32);
            for (int i = start; i < end; i++) {
                #pragma HLS pipeline
                ciao_stream << ciao[i];
            }
        }

        if (done_empty != 1 && rpao_empty == 1) {
            done = rpao_done_stream.read();
        }
    }

    ciao_done_stream << 1;
}

Note that you only need to optimize in terms of memory, parallelism optimization is not necessary.
You can add cache mechanism to remove redundant memory accesses. Consider tag, index and tag in cache addressing.
Return the complete optimized code.
"""


DETERMINE_CONTINUE_SPLIT_TEST = \
"""
You are an FPGA engineer and you are designing an accelerator using HLS(high-level-synthesis).
Here is a software code. Your goal is to optimize this code to make it work more efficiently on FPGA.

Splitting the code into multiple stages and performing those stages in a pipeline format is a common optimization approach in HLS code. However, some code is not suitable for further splitting due to its overly simple process or inconvenient parallel execution. Some code processes are more complex, or there are parts that can be executed in parallel during the execution process, so they can be further split. Please check if the following code can be further split:

static void bfs_kernel(
    char        *depth, 
    const int   *rpao, 
    const int   *ciao, 
    int         *frontier_size, 
    int         vertex_num, 
    const char  level, 
    const char  level_plus1
) {
    char d;
    int start, end;
    int ngb_vidx;
    char ngb_depth;
    int counter = 0;
    for (int i = 0; i < vertex_num; i++) {
        d = depth[i];
        if (d == level) {
            counter++;
            start = rpao[i];
            end = rpao[i + 1];
            for (int j = start; j < end; j++) {
                ngb_vidx = ciao[j];
                ngb_depth = depth[ngb_vidx];
                if (ngb_depth == -1) {
                    depth[ngb_vidx] = level_plus1;
                }
            }
        }
    }
    *frontier_size = counter;
}

Please return the results without telling me the specific splitting method. Your answer can only be yes or no.
"""

CONTINUE_SPLIT_TEST = \
"""
You are an FPGA engineer and you are designing an accelerator using HLS(high-level-synthesis).
Here is a software code for bfs, which serially implements the bfs algorithm. Your goal is to optimize this code to make it work more efficiently on FPGA.

Dividing the algorithm into multiple stages enables Vivado HLS to generate an implementation method that allows different stages of the algorithm to run on different datasets. This optimization method uses dataflow instructions, called task pipelining, which is very common and suitable for various hardware optimization methods. 

The following function is a part of the whole algorithm process. This function can be further broken down into multiple stages. Please split it into more than one stages. Represent each stage with a function, paying attention to the parameter interfaces between the functions.

// Stage 2: Calculation of contributions for each vertex
void calculate_contributions(
    int *rpao,
    int *ciao,
    float *pr,
    float new_pr[],
    int vertex_num
) {
#pragma HLS INLINE off
    calculate_loop: for (int i = 0; i < vertex_num; i++) {
        int start = rpao[i];
        int end = rpao[i + 1];
        int degree = end - start;  // Degree of the vertex, used to normalize contribution
        for (int j = start; j < end; j++) {
            int ngb_idx = ciao[j];
            float contribution = pr[i] / degree;
            // Critical section - needs atomic or parallel-safe add
            new_pr[ngb_idx] += contribution;
  
      }
    }
}

Here are some general suggestions to guide you through the process of partitioning the code for maximizing algorithm parallelism using task pipelining:

1. For loop blocks in the code, you can split them based on the granularity of the loops that can be executed in parallel. The following are some examples:
    - Each iteration of the loop is treated as a stage: 
    In merge sorting, the original code processes intervals of the same width int each iteration, so intervals of lengths such as 2, 4, and 8 can be considered as one stage respectively.

        // before:
        for (int width = 1; width < SIZE; width = 2 * width) {
        merge_arrays:
            for (int i1 = 0; i1 < SIZE; i1 = i1 + 2 * width) {
                int i2 = i1 + width;
                int i3 = i1 + 2 * width;
                if (i2 >= SIZE) i2 = SIZE;
                if (i3 >= SIZE) i3 = SIZE;
                merge(A, i1, i2, i3, temp);
            }
        }

        // after:
        for (int stage = 1; stage < STAGES - 1; stage++) {
            merge_arrays(temp[stage - 1], width, temp[stage]);
            width *= 2;
        }

    - The traversal of the first and second half of the loop is considered as a stage:
    In histogram statistics, since the first and second halves of the loop can be executed in parallel, they are considered as two stages.

        // before:
        void histogram(int in[INPUT_SIZE], int hist[VALUE_SIZE]) {
            int val;
            for (int i = 0; i < INPUT_SIZE; i++) {
                val = in[i];
                hist[val] = hist[val] + 1;
            }
        }

        // after:
        void histogram_parallel(int in1[INPUT_SIZE/2], int in2[INPUT_SIZE/2], int hist[VALUE_SIZE]) {
            int hist1[VALUE_SIZE];
            int hist2[VALUE_SIZE];

            histogram_map(in1, hist1);
            histogram_map(in2, hist2);
            histogram_reduce(hist1, hist2, hist);
        }

    - Each layer loop is considered as a stage:
    In the following BFS algorithm, there are two loops, with the first loop used to find the frontier vertex and read the corresponding rpao data, the second loop used to traverse the neighbors of the frontier vertex, which can be divided into two stages based on this. These two stages can be further divided into multiple stages.

        // before:
        static void bfs_kernel(
            char *depth, const int *rpao, const int *ciao, 
            int  *frontier_size, int vertex_num, const char level, 
            const char level_plus1
        ) {
            int start, end;
            int ngb_vidx;
            char ngb_depth;
            int counter = 0;
            loop1: for (int i = 0; i < vertex_num; i++) {
                char d = depth[i];
                if (d == level) {
                    counter++;
                    start = rpao[i];
                    end = rpao[i + 1];
                    loop2: for (int j = start; j < end; j++) {
                        ngb_vidx = ciao[j];
                        ngb_depth = depth[ngb_vidx];
                        if (ngb_depth == -1) {
                            depth[ngb_vidx] = level_plus1;
                        }
                    }
                }
            }
            *frontier_size = counter;
        }

        // after: (Pseudocode representation) read_frontier_vertex() and read_rpao represent loop1, traverse represent loop2
        void read_frontier_vertex(...) {
            for (int i = 0; i < vertex_num; i++) {
                if (d == level) {
                    frontier_stream << i;
                }
            }
        }
        void read_rpao(...) {
            while (!frontier_stream.empty()) {
                int idx   = frontier_stream.read();
                int start = rpao[idx];
                int end   = rpao[idx + 1];
                start_stream << start;
                end_stream   << end;
            }
        }
        void traverse() {
            while (!start_stream.empty() && !end_stream.empty()) {
                int start = start_stream.read();
                int end   = end_stream.read();
                for (int j = start; j < end; j++) {
                    ngb_vidx = ciao[j];
                    ngb_depth = depth[ngb_vidx];
                    if (ngb_depth == -1) {
                        depth[ngb_vidx] = level_plus1;
                    }
                }
            }
        }

    - Multiple layers of loops work together to form a stage:
    In video frame image convolution, there are a total of 4 layers of loops, where loop1 and loop2 are considered as the stages for reading the pixel, and loop3 and loop4 are the stages for calculating the convolution.

        loop1: for(int line = 0; line < img_height; ++line) {
            loop2: for(int pixel = 0; pixel < img_width; ++pixel) {
                float sum_r = 0, sum_g = 0, sum_b = 0;

                loop3: for(int m = 0; m < coefficient_size; ++m) {
                    loop4: for(int n = 0; n < coefficient_size; ++n) {
                        int ii = line + m - center;
                        int jj = pixel + n - center;
                        if(ii >= 0 && ii < img_height && jj >= 0 && jj < img_width) {
                            sum_r += inFrame[(ii * img_width) + jj].r * coefficient[(m * coefficient_size) + n];
                            sum_g += inFrame[(ii * img_width) + jj].g * coefficient[(m * coefficient_size) + n];
                            sum_b += inFrame[(ii * img_width) + jj].b * coefficient[(m * coefficient_size) + n];
                        }
                    }
                }
                outFrame[line * img_width + pixel].r = fabsf(sum_r);
                outFrame[line * img_width + pixel].g = fabsf(sum_g);
                outFrame[line * img_width + pixel].b = fabsf(sum_b);
            }
        }

2. For non-loop blocks in the code, they can be split based on the functionality.

Please split the code according to the above guidelines, and when splitting loop blocks, please indicate which of the above four examples the split method refers to.
"""
