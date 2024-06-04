TASK_PIPELINE_PROMPT = \
"""
Dividing the algorithm into multiple stages enables Vivado HLS to generate an implementation method that allows different stages of the algorithm to run on different datasets. This optimization method uses dataflow instructions, called task pipelining, which is very common and suitable for various hardware optimization methods. Please represent each stage with a function, paying attention to the parameter interfaces between the functions.
"""

TASK_PIPELINE_FOR_SINGLE_FUNCTION_PROMPT = \
"""
Dividing the algorithm into multiple stages enables Vivado HLS to generate an implementation method that allows different stages of the algorithm to run on different datasets. This optimization method uses dataflow instructions, called task pipelining, which is very common and suitable for various hardware optimization methods. 

The following function is a part of the whole algorithm process. This function can be further broken down into multiple stages. Please split it into more than one stages.
"""

# split strategy 1: read-compute-write
TASK_PIPELINE_STRATEGY_PROMPT = \
"""
You can consider partitioning the code into a Load-Compute-Store pattern:
1.read_dataflow: Read the data.
2.compute_dataflow: Process the data.
3.write_dataflow: Write the output to the main memory. 
Please return the complete code.
"""

# split strategy 2: analyze-identify dependency-determine parallel
TASK_PIPELINE_STRATEGY_PROMPT_2 = \
"""
Please follow the following steps to partition the code:
step1: Analyze program data flow
step2: Identify data dependencies between stages
step3: Determine which processes can be executed in parallel or in pipeline
"""

# split strategy 3: 
#  1.identify independent stages
#  2.identify dependencies
#  3.pipeline initialization and cleanup
TASK_PIPELINE_STRATEGY_PROMPT_3 = \
"""
Here are some general steps to guide you through the process of partitioning the code for maximizing algorithm parallelism using task pipelining:
1.Identify independent stages: 
    - Look for stages in the algorithm that are independent and do not have data dependencies between them. These stages can be executed concurrently
    - For example, consider a loop-intensive algorithm. Identify loops that do not have dependencies on each other and can be executed in parallel
2.Identify dependencies:
    - Identify dependencies between stages to understand the order in which they should be executed
    - For example, if Stage B depends on the output of Stage A, you need to ensure that Stage A completes before Stage B starts.
3.Pipeline initialization and cleanup:
    - If there are initialization or cleanup stages in your algorithm, consider whether these can be pipelined as well.
    - For example, if your algorithm requires some setup before processing data, see if this setup can be done concurrently with other stages.
"""

# split strategy 4:
# parallel-granularity-based splitting method for loop blocks
TASK_PIPELINE_STRATEGY_PROMPT_4 = \
"""
Here are some general suggestions to guide you through the process of partitioning the code for maximizing algorithm parallelism using task pipelining:

1. For loop blocks in the code, you can split them based on the granularity of the loops that can be executed in parallel. First identify what each layer of loop execution is doing, and then divide them according to the granularity that can be parallelized. The following are some examples:
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

Please remember the following rules:
1. Split the code according to the above guidelines, and when splitting loop blocks, please indicate which of the above four examples the split method refers to.
2. Represent each stage with a function, and pay attention to the parameter interfaces between the functions.
3. Do not modify the interface of the top-level function
4. Divide the code as thoroughly as possible
"""

# determine whether the code can be further split
DETERMINE_CONTINUE_SPLIT = \
"""
Splitting the code into multiple stages and performing those stages in a pipeline format is a common optimization approach in HLS code. However, some code is not suitable for further splitting due to its overly simple process or inconvenient parallel execution. Some code processes are more complex, or there are parts that can be executed in parallel during the execution process, so they can be further split. Please check if the following code can be further split:
{CODE_CONTENT}
"""