PRAGMA_INFO_EXTRACT_PROMPT = \
"""
The following is a document explaining the use of pragma HLS {pragma_name} in HLS (high level synthesis):

{pragma_document_content}

Please help me summarize the usage of this pragma, including its function introduction, applicable scenarios, parameter descriptions, and usage examples. The results are presented in the following way:

Pragma HLS allocation

Function Introduction:

Applicable scenarios:

Parameter Description:

Usage example:
"""

# pragma HLS allocation
ALLOCATION_PROMPT = \
"""
pragma HLS allocation

Function Overview: 
pragma HLS allocation is a compilation directive to restrict the allocation of hardware resources within implemented kernels. It allows users to specify the number of instances to be limited in functions, loops, or code regions, thereby controlling resource usage in the generated hardware design.

Application Scenes: 
- When there is a need to limit the number of hardware resource instances in specific functions, loops, or code regions for optimizing either resource utilization or performance.
- In scenarios where there are multiple instances in the design, controlling resource usage by limiting the instance count for hardware-level optimization.
"""

ALLOCATION_DEMO = \
"""
Parameter Description:
- instances=<list>: Specifies the names of functions, operators, or kernels to be restricted.
- limit=<value>: An optional parameter specifying the limit on the number of instances to be used in the kernel.
- <type>: Specifies the type of allocation applied to functions, operations, or kernels used in creating the design. It can be "function," "operation," or "core."
    - function: Applies allocation to functions listed in the instance list.
    - operation: Applies allocation to operations listed in the instance list.
    - core: Applies allocation to kernels specified in the instance list, representing specific hardware components used in design creation.

Usage Examples: 
- Limit the number of function instances in the RTL of a hardware kernel to 2:
```cpp
#pragma HLS allocation instances=foo limit=2 function
```
"""

# pragma HLS resource
RESOURCE_PROMPT = \
"""
pragma HLS resource

Function Overview:
pragma HLS resource is one of the compilation directives to specify particular library resources (cores) for implementing variables (arrays, arithmetic operations, or function parameters) in RTL. Users can control which core to use to implement operations in the code using this pragma. 

Application Scenes:
- When there is a need to explicitly specify a particular core from the library for implementing a specific operation.
- In scenarios where multiple cores are available for implementing the same functionality, choosing the appropriate core through this pragma to meet performance or resource optimization requirements.
- Controlling whether an array is implemented as a single-port RAM or dual-port RAM.
"""

RESOURCE_DEMO = \
"""
Parameter Description: 
- variable=<variable>: Specifies the variable, array, arithmetic operation, or function parameter to which the resource pragma should be assigned.
- core=<core>: Specifies the name of the core, as defined in the technology library. Obtain the list of available cores using the list_core command.
- latency=<int>: Optional parameter specifying the latency of the core. Allows users to model off-chip non-standard SRAM with a latency of 2 or 3 on the interface, or to use more pipeline stages for internal operations to address timing issues.

Usage Examples:
1. In the example below, a 2-stage pipeline multiplier is specified to implement the multiplication of the variable c in the function foo. The implementation of variable d is determined by Vivado HLS.
```cpp
int foo(int a, int b) {
    int c, d;
    #pragma HLS RESOURCE variable=c latency=2
    c = a * b;
    d = a * c;
    return d;
}
```

2. In the example below, the variable coeffs[128] is a parameter of the top-level function foo_top. This example specifies using the core RAM_1P from the library to implement the coefficients.
```cpp
#pragma HLS resource variable=coeffs core=RAM_1P  
```
"""

# pragma HLS inline
INLINE_PROMPT = \
"""
pragma HLS inline

Function Overview:
pragma HLS inline is a compilation directive to control the inlining behavior of functions. Inlining removes functions as separate entities in the hierarchy by inserting the code of the called function directly at the call site, eliminating the need for a separate hierarchy. This directive allows users to selectively enable or disable inlining for functions and specify the scope and recursion level of inlining.

Application Scenes:
- When eliminating the hierarchy of function calls in RTL generation to improve code execution efficiency and sharing optimization.
- In scenarios where control over the scope and recursion level of inlined functions is needed to meet optimization requirements for performance or resource utilization.
- While optimizing the results, it also increases the runtime. If you want to achieve better performance, you need to set inline off to cancel inline.
"""

INLINE_DEMO = \
"""
Parameter Description:
- region: An optional parameter specifying that all functions within the specified region will be inlined. Applicable to the scope of the region.
- recursive: By default, only a single-level function inline is performed, specifying that functions within the inlined function are not inlined. Using this parameter allows for the recursive inlining of all functions within the specified function or region.
- off: Disables function inlining, preventing specific functions from being automatically inlined when all other functions are inlined. Useful for preventing the automatic inlining of small functions.

Usage Examples:
1. In the example below, all functions within the foo_top body will be inlined, but any lower-level functions within these functions will not be inlined.
```cpp
void foo_top { a, b, c, d} { 
#pragma HLS inline region 
...
```

2. In the example below, all functions within the foo_top body will be recursively inlined, but the function foo_sub will not be inlined. The recursive compilation directive is placed in the foo_top function, and the inline-off compilation directive is placed in the foo_sub function.
```cpp
void foo_sub (p, q) { 
#pragma HLS inline off 
int q1 = q + 10; 
foo(p1,q);// foo_3 
...
}

void foo_top { a, b, c, d} {
    #pragma HLS inline region recursive
    ...
    foo(a,b);//foo_1
    foo(a,c);//foo_2
    foo_sub(a,d);
    ...
```

3. In the example below, the copy_output function will be inlined into any calling function or region.
```cpp
void copy_output(int *out, int out_lcl[OSize * OSize], int output) {
#pragma HLS INLINE
    // Calculate each work_item's result update location
    int stride = output * OSize * OSize;
    
    // Work_item updates output filter/image in DDR
    writeOut: for(int itr = 0; itr < OSize * OSize; itr++) {
        #pragma HLS PIPELINE
        out[stride + itr] = out_lcl[itr];
    }
```
"""

# pragma HLS function_instantiate
FUNCTION_INSTANTIATE_PROMPT = \
"""
pragma HLS function_instantiate

Overview:
pragma HLS function_instantiate directive is a compilation directive to optimize function instantiation, aiming to improve performance and reduce resource utilization. This directive allows the creation of unique hardware descriptions for each instance of a function, enabling targeted local optimizations. By default, all instances of the same function share a hardware implementation, but using this directive facilitates local optimizations for each instance.

Application Scenes:
- It is applicable when the same function has different constant parameter values in various instance calls. This directive helps generate independent hardware implementations for each instance, optimizing performance.
- When there is a need to reduce the complexity of control logic while improving latency and throughput, using this directive effectively utilizes hardware resources.
"""

FUNCTION_INLINE_DEMO = \
"""
Parameter Description:
- variable=<variable>: Specifies the function parameter for which instantiation optimization is required. This parameter is treated as a constant in each function instance call. Performing local optimizations on this parameter contributes to generating smaller and more efficient hardware implementations.

Usage Example:
1. In the following example, #pragma HLS function_instantiate is used to optimize the instantiation of the foo_sub function. This results in generating independent hardware implementations for each different incr parameter value, thereby improving overall performance.
```cpp
char foo_sub(char inval, char incr) { 
#pragma HLS function_instantiate variable=incr 
return inval + incr; 
} 

void foo(char inval1, char inval2, char inval3, 
         char *outval1, char *outval2, char *outval3) { 
    *outval1 = foo_sub(inval1, 1); 
    *outval2 = foo_sub(inval2, 2); 
    *outval3 = foo_sub(inval3, 3); 
}
```
"""

# pragma HLS stream
STREAM_PROMPT = \
"""
pragma HLS stream

Function Overview:
pragma HLS stream is a compilation directive to specify the implementation approach for array variables. By default, arrays are implemented as RAM, but this directive allows the choice of implementing arrays as a streaming interface using FIFOs instead of RAM, offering a more efficient communication mechanism.

Application Scenes:
- It is applicable when dealing with data stored in arrays that is used or generated in a sequential manner, as using streaming data instead of RAM can enhance communication efficiency.
- It can be used when there is a need to reduce the depth of the FIFO in the data flow channel to decrease resource utilization.
"""

STREAM_DEMO = \
"""
Parameter Description:
- variable=<variable>: Specifies the name of the array to be implemented as a streaming interface.
- depth=<int>: Relevant to data flow channels. Allows modification of the FIFO size and specifies a different depth. In the data flow region, the depth option is commonly used to reduce the FIFO size, especially when all loops and functions process data at a rate of II=1.
- dim=<int>: Specifies the dimension of the array to be streamed. The default is dimension 1.
- off: Disables streaming data, i.e., uses RAM instead of FIFO.

Usage Examples:
1. Implement array A[10] as a streaming FIFO
```cpp
#pragma HLS STREAM variable=A
```

2. Implement array B as a streaming FIFO with a depth of 12
```cpp
#pragma HLS STREAM variable=B depth=12
```

3. Disable streaming for array C, in this example, assuming config_dataflow is enabled
```cpp
#pragma HLS STREAM variable=C off
```
"""

# pragma HLS pipeline
PIPELINE_PROMPT = \
"""
pragma HLS pipeline

Function Overview:
pragma HLS pipeline is a compilation directive to reduce the initiation interval of functions or loops, thereby improving performance through concurrent execution of operations. It allows the pipelining of operations in functions or loops to process new inputs every N clock cycles, where N is the initiation interval (II) of the loop or function. The default II is 1, meaning a new input is processed every clock cycle.

Application Scenes:
- It is suitable for scenarios where reducing the initiation interval of functions or loops is desired to enhance concurrent performance.
- It is applicable for optimizing performance by pipelining loops to enable concurrent execution of operations.
"""

PIPELINE_DEMO = \
"""
Parameter Description:
- II=<int>: Specifies the desired initiation interval for pipelining operations. Vivado HLS attempts to meet this requirement, but the actual result may be affected by data dependencies and may have a larger initiation interval. The default value is 1.
- enable_flush: An optional keyword used to implement pipelining, where the pipeline flushes and clears if the active data on the pipeline inputs becomes inactive. This feature is only supported for pipelined functions and is not supported for pipelined loops.
- rewind: An optional keyword that enables rewinding or continuous loop pipelining without pausing between one loop iteration's end and the beginning of the next. It is effective only when there is a single loop (or perfectly nested loops) in the top-level function. This feature is only supported for pipelined loops and is not supported for pipelined functions.

Usage Example:
1. Pipelining function foo with an initiation interval of 1, in this example, by using #pragma HLS pipeline, the function foo is pipelined, enabling concurrent execution of operations to improve performance.
```c
void foo { a, b, c, d} { 
    #pragma HLS pipeline II=1 
    // ...
}
```
"""

# pragma HLS occurrence
OCCURRENCE_PROMPT = \
"""
pragma HLS Occurrence

Function Overview:
pragma HLS occurrence is used to specify that the code within a particular region has a lower execution frequency compared to the enclosing loop or function. This pragma allows for more efficient pipelining of code with lower execution frequency, potentially enabling sharing in the top-level pipeline.

Application Scenes:
- It is suitable for specific regions within loops or functions where the execution frequency is lower than that of the enclosing loop or function.
"""

OCCURRENCE_DEMO = \
"""
Parameter Description:
- cycle=<int>: Specifies the occurrence count N/M. Here, N is the number of times the enclosing function or loop is executed, and M is the number of times the conditional region is executed. N must be an integer multiple of M.

Usage Example:
1. In the following example, the execution frequency of the Cond_Region is one-fourth of the surrounding code, indicating that the internal code is pipelined at a slower rate.
```cpp
Cond_Region: { 
#pragma HLS occurrence cycle=4 
...
}
```
"""

# pragma HLS unroll
UNROLL_PROMPT = \
"""
pragma HLS unroll

Function Overview:
pragma HLS unroll is a compilation directive to unroll loops, creating multiple independent operations instead of a single operation set. The UNROLL compilation directive transforms loops by creating multiple copies of the loop body in the RTL design, allowing parallel execution of some or all loop iterations.

Application Scenes:
- When increased loop parallelism is desired to enhance performance and throughput.
- When optimizing hardware implementation to execute multiple loop iterations in the same clock cycle.
"""

UNROLL_DEMO = \
"""
Parameter Description:
- factor=<N>: Specifies a non-zero integer N, indicating a request for partial unrolling. The loop body will be repeated the specified number of times, adjusting iteration information accordingly. If factor= is not specified, the loop will be fully unrolled.
- region: An optional keyword used to unroll all loops within a specified loop body (region) without unrolling the enclosing loop itself.
- skip_exit_check: An optional keyword applicable only when partial unrolling is specified with factor=. It indicates whether to skip the exit condition check. If the iteration count of the loop is known and is a multiple of the factor, skip_exit_check can be used to eliminate exit checks and related logic.

Usage Examples:
1.Fully unroll a loop:
```cpp
for(int i = 0; i < X; i++) {
    #pragma HLS unroll
    a[i] = b[i] + c[i];
}
```

2. Partially unroll a loop (unroll factor of 2 with exit check skipped):
```cpp
for(int i = 0; i < X; i++) {
    #pragma HLS unroll factor=2 skip_exit_check
    a[i] = b[i] + c[i];
}
```

3. Fully unroll all loops within a specified region:
```cpp
void foo(int data_in[N], int scale, int data_out1[N], int data_out2[N]) {
    int temp1[N];
    loop_1: for(int i = 0; i < N; i++) {
        #pragma HLS unroll region
        temp1[i] = data_in[i] * scale;
        loop_2: for(int j = 0; j < N; j++) {
            data_out1[j] = temp1[j] * 123;
        }
        loop_3: for(int k = 0; k < N; k++) {
            data_out2[k] = temp1[k] * 456;
        }
    }
}
```
"""

# pragma HLS dependence
DEPENDENCE_PROMPT = \
"""
pragma HLS dependence

Function Overview:
pragma HLS dependence is a compilation directive used to control loop dependencies. This directive provides additional information to overcome loop carry dependencies, allowing for loop pipelining or pipelining with lower intervals to optimize hardware performance.

Application Scenes:
- It is used when automatic dependency detection by Vivado HLS is inaccurate or overly conservative.
- It is employed in cases where there are complex dependencies within or between different loop iterations, and precise control is needed.
"""

DEPENDENCE_DEMO = \
"""
Parameter Description:
- variable=<variable>: (Optional) Specifies the variable for which dependencies should be considered.
- <class>: Optionally specifies the variable class for which dependencies need clarification, with valid values including array or pointer.
- <type>: Specifies whether the dependency is intra (within the same loop iteration) or inter (between different loop iterations).
- <direction>: Specifies the direction of the dependency, with valid values being RAW, WAR, or WAW.
- distance=<int>: Specifies the iteration distance for array accesses, relevant only for loop carry dependencies.
- <dependent>: Specifies whether enforcement (true) or removal (false) of dependencies is required, with the default value being true.

Dependency Examples:
1. Loop independent dependency: Access the same elements within the same loop iteration.
for (i=0; i<N; i++){
    A [i]=x;
    Y=A [i];
}

2. Loop carry dependency: Accessing the same element in different loop iterations.
for (i=0; i<N; i++){
    A [i]=A [i-1] * 2;
}

Usage Examples:
1. Declare no dependencies between loop iterations. Vivado HLS is unaware of the value of cols and conservatively assumes writing buff_A[1][cols] and read buff_A[1][cols]. There is always a dependency relationship between reading and writing. In such an algorithm, cols is unlikely to be zero, but Vivado HLS cannot make assumptions about data dependencies. To overcome this flaw, you can use the DEPENDENCE compilation directive to declare that there are no dependencies between loop iterations
```cpp
void foo(int rows, int cols, ...)
{
    for (row = 0; row < rows + 1; row++) {
        for (col = 0; col < cols + 1; col++) {
            #pragma HLS PIPELINE II=1
            #pragma HLS dependence variable=buff_A inter false
            #pragma HLS dependence variable=buff_B inter false
            if (col < cols) {
                buff_A[2][col] = buff_A[1][col]; // read from buff_A[1][col]
                buff_A[1][col] = buff_A[0][col]; // write to buff_A[1][col]
                buff_B[1][col] = buff_B[0][col];
                temp = buff_A[0][col];
            }
        }
    }
}
```

2. Remove dependencies between Var1 within the same iteration
```cpp
#pragma HLS dependence variable=Var1 intra false
```

3. Declare RAW dependencies for all arrays within the loop iteration
```cpp
#pragma HLS dependence array intra RAW true
```
"""

# pragma HLS loop_flatten
LOOP_FLATTEN_PROMPT = \
"""
pragma HLS loop_flatten

Function Overview:
The pragma HLS loop_flatten allows the flattening of nested loops into a single loop hierarchy to improve latency. Flattening nested loops can reduce clock cycles, enabling greater optimization of loop body logic, particularly in RTL (Register-Transfer Level) implementations.

Application Scenes:
- Applicable to perfect and imperfect loops where only the innermost loop contains loop body content.
- No specified logic between loop statements.
- All loop boundaries are constants.
- For imperfect loops, the outermost loop boundary can be a variable.
"""

LOOP_FLATTEN_DEMO =\
"""
Parameter Description:
- off: An optional keyword used to prevent flattening. It can prevent flattening specific loops when flattening other loops at specified locations.

Usage Example:
1. pragma HLS loop_flatten is used to flatten the loop_1 and all loops above it in the function foo
```cpp
void foo (num_samples, ...) { 
    int i; ...
    loop_1: for(i=0; i < num_samples; i++) { 
        #pragma HLS loop_flatten 
        ...
        result = a + b; 
    }
}
```

2. by using the off parameter, flattening of loops in loop_1 is prevented.
```cpp
loop_1: for(i=0; i < num_samples; i++) {
    #pragma HLS loop_flatten off
    ...
}
```
"""

# pragma HLS loop_merge
LOOP_MERGE_PROMPT = \
"""
pragma HLS loop_merge

Function Overview:
The pragma HLS loop_merge is used to merge consecutive loops into a single loop, reducing overall latency, promoting sharing, and improving logic optimization. Loop merging aims to decrease the number of clock cycles needed for transitions between loop body implementations in RTL (Register-Transfer Level) and allows for parallel implementation of loops.

Application Scenes:
- Applicable to consecutive loops where loop boundaries have the same values or share the maximum constant value.
- Suitable for loops where it can be ensured that the loop body code does not have one-sided effects and produces the same results upon multiple executions.
"""

LOOP_MERGE_DEMO = \
"""
Parameter Description:
- force (optional keyword): Used to forcefully merge loops even if Vivado HLS issues a warning. In this case, manual assurance is required to ensure the merged loops function correctly.

Usage Example:
1. pragma HLS loop_merge is used to merge all consecutive loops in the function foo into a single loop
```cpp
void foo (num_samples, ...) {
    #pragma HLS loop_merge
    int i;
    ...
    loop_1: for(i=0; i < num_samples; i++) {
        // Loop body
    }
}
```

2. by using the force keyword, all loops inside loop_2 are forcefully merged, not just loop_2 itself
```cpp
loop_2: for(i=0; i < num_samples; i++) { 
    #pragma HLS loop_merge force 
    // Loop body
}
```
"""

# pragma HLS loop_tripcount
LOOP_TRIPCOUNT_PROMPT = \
"""
pragma HLS loop_tripcount

Function Overview:
pragma HLS loop_tripcount is used to manually specify the total number of iterations for a loop. It aids the tool in analysis without affecting the synthesis results. This directive allows users to specify the minimum, maximum, and average iteration counts for a loop, enabling synthesis analysis and optimization in cases where the loop iteration count is unknown or cannot be determined dynamically.

Application Scenes:
- When Vivado HLS cannot determine the iteration count of a loop, especially for variables dependent on input parameters or dynamically computed operations.
- In situations requiring manual specification of loop iteration counts for synthesis analysis and optimization.
"""

LOOP_TRIPCOUNT_DEMO = \
"""
Parameter Description:
- min=<int>: Specifies the minimum number of loop iterations.
- max=<int>: Specifies the maximum number of loop iterations.
- avg=<int>: Specifies the average number of loop iterations.

Usage Example:
1. the loop_1 loop has a minimum iteration count of 12 and a maximum iteration count of 16. This helps the Vivado HLS tool analyze how loop delay impacts the overall design delay and aids in determining appropriate design optimizations
```cpp
void foo (int num_samples, ...) {
    int i;
    ...
    loop_1: for(i=0; i < num_samples; i++) {
        #pragma HLS loop_tripcount min=12 max=16
        ...
        result = a + b;
    }
}
```
"""

# pragma HLS array_map
ARRAY_MAP_PROMPT = \
"""
pragma HLS array_map

Function Overview:
pragma HLS array_map is used to combine multiple smaller arrays into a larger array, optimizing the utilization of block RAM resources. It supports two mapping methods: horizontal mapping, where original array elements are connected to create a new array, and vertical mapping, where array fields are connected to form a new array. The main purpose of this compilation directive is to more efficiently utilize block RAM units in FPGA physically.

Application Scenes:
- When there are multiple smaller arrays.
- When the use of block RAM needs to be optimized in the FPGA design, especially if the target hardware supports block RAM or UltraRAM.
"""

ARRAY_MAP_DEMO = \
"""
Parameter Description:
- variable=<name>: Specifies the array variable to be mapped to the new target array `<instance>`.
- instance=<instance>: Specifies the name of the new array that combines the arrays.
- <mode>: Optionally specifies the mapping of the array as horizontal or vertical.
  - Horizontal mapping is the default `<mode>`, connecting arrays to form a new array with more elements.
  - Vertical mapping concatenates arrays to create a new array with a longer word size.
- offset=<int>: Applicable only for horizontal array mapping. The offset specifies an integer value offset to apply before mapping the array to the new array `<instance>`.

Usage Examples:
1. Horizontal Mapping
```cpp
void foo (...) { 
    int8 array1[M]; 
    int12 array2[N]; 
    #pragma HLS ARRAY_MAP variable=array1 instance=array3 horizontal 
    #pragma HLS ARRAY_MAP variable=array2 instance=array3 horizontal 
    // ...
    loop_1: for(i=0;i<M;i++) { 
        array1[i] = ...; 
        array2[i] = ...; 
        // ...
    } 
    // ...
}
```

2. Horizontal Mapping, Arrays A[10] and B[15] are horizontally mapped to a single new array AB[25]
```cpp
#pragma HLS array_map variable=A instance=AB horizontal  
#pragma HLS array_map variable=B instance=AB horizontal 
```

3. Vertical Mapping, Concatenate arrays C and D vertically into a new array CD, merging the bit widths of C and D
```cpp
#pragma HLS array_map variable=C instance=CD vertical  
#pragma HLS array_map variable=D instance=CD vertical 
```
"""

# pragma HLS array_partition
ARRAY_PARTITION_PROMPT = \
"""
pragma HLS array_partition

Function Overview:
This pragma is used to partition arrays, dividing them into smaller arrays or individual elements. The partitioning results in generating multiple small memories or registers at the RTL (Register-Transfer Level) instead of a single large memory. This effectively increases the number of read and write ports, potentially enhancing the design's throughput.

Application Scenes:
- When there is a need to increase the number of storage read and write ports to enhance parallelism and throughput.
- Optimizing multi-dimensional arrays in HLS designs, especially in array operations within processors.
"""

ARRAY_PARTITION_DEMO = \
"""
Parameter Description:
- variable=<name>: Specifies the required parameter, the array variable to be partitioned.
- <type>: Optionally specifies the partition type, including cyclic, block, and complete (default type).
- factor=<int>: Specifies the number of smaller arrays to create. Not required for complete partitioning but necessary for block and cyclic partitioning.
- dim=<int>: Specifies which dimension of a multi-dimensional array to partition. 0 indicates all dimensions, and a non-zero value indicates partitioning only the specified dimension.

Usage Examples:
1. Partition an array AB[13] with 13 elements into four arrays, where three arrays have three elements each, and one array has four elements:
```cpp
#pragma HLS array_partition variable=AB block factor=4
```

2. Partition the second dimension of a two-dimensional array AB[6][4] into two new dimensions [6][2]:
```cpp
#pragma HLS array_partition variable=AB block factor=2 dim=2
```

3. Partition the second dimension of a two-dimensional array in_local into individual elements:
```cpp
int in_local[MAX_SIZE][MAX_DIM];
#pragma HLS ARRAY_PARTITION variable=in_local complete dim=2
```
"""

# pragma HLS array_reshape
ARRAY_RESHAPE_PROMPT = \
"""
pragma HLS array_reshape

Function Overview:
The array_reshape pragma is used to reshape arrays by combining the effects of array partitioning and vertical array mapping. It allows breaking down arrays into smaller ones while connecting array elements by increasing the bit width to enhance parallel access and enable access to more data within a single clock cycle. This directive creates a new array with fewer elements but a larger bit width.

Application Scenes:
- When optimizing parallel access to arrays for improved performance.
- In cases where reducing the number of block RAMs is needed while maintaining efficient access to arrays.
- When reshaping arrays to meet specific hardware constraints.
"""

ARRAY_RESHAPE_DEMO = \
"""
Parameter Description:
- variable=<name>: A required parameter specifying the array variable to be reshaped.
- type: An optional parameter specifying the partition type, with the default being complete. Supported types include cyclic, block, and complete.
- factor=<int>: Specifies the number by which the current array is divided (or the number of temporary arrays to be created).
- dim=<int>: Specifies which dimension of a multi-dimensional array to partition. 0 indicates partitioning all dimensions, while a non-zero value indicates partitioning only the specified dimension.

Usage Examples:
1. Use block mapping to reshape (partition and map) an 8-bit array AB[17] with 17 elements into a new 32-bit array with five elements. 
```cpp
#pragma HLS array_reshape variable=AB block factor=4
```
factor = 4 indicates that the array should be divided into four copies.Therefore, the 17 elements were reshaped into an array of 5 elements, and the bit width was four times.In this case, the last element AB [17] is mapped to the low eight bits of the fifth element, while the rest of the fifth element is empty.

2. Reshape the two-dimensional array AB[6][4] into a new array of dimension [6][2], where dimension 2 has twice the bit width
```cpp
#pragma HLS array_reshape variable=AB block factor=2 dim=2  
```

3. Reshape the 3D 8-bit array AB[4][2][2] in function foo into a new set of elements (a register),128 bits wide (4*2*2*8)
```cpp
#pragma HLS array_reshape variable=AB complete dim=0
```
dim = 0 indicates all the dimensions of reshaping the array
"""

# pragma HLS data_pack
DATA_PACK_PROMPT = \
"""
pragma HLS data_pack

Function Overview:
pragma HLS data_pack is a compilation directive to pack data fields of a structure into a scalar with a wider bit width. This helps reduce the memory required for variables while allowing simultaneous read and write access to all members of the structure. It is used in hardware design to optimize memory access and data storage.

Application Scenes:
- Optimize the memory layout of structures to reduce storage space requirements.
- Improve memory access efficiency, allowing simultaneous read and write access to all members of a structure.
- In hardware design, especially in FPGA design, optimize data storage and access.
"""

DATA_PACK_DEMO = \
"""
Parameter Description:
- variable=<variable>: Specifies the structure variable to be packed.
- instance=<name>: Optional parameter that specifies the name of the resulting variable after packing. If not specified, the name of the input variable is used.
- <byte_pad>: Optional parameter specifying whether to pack data on 8-bit boundaries. Supports two values:
  - struct_level: Pack the entire structure first and then pad up to the next 8-bit boundary.
  - field_level: First pad each individual element (field) of the structure on an 8-bit boundary and then pack the structure.

Usage Examples:
1. Pack a structure array AB[17] with three 8-bit fields (R, G, B) into a new 24-bit array with 17 elements.
```cpp
typedef struct {
    unsigned char R, G, B;
} pixel;
pixel AB[17];
#pragma HLS data_pack variable=AB
```

2. Pack a structure pointer AB with three 8-bit fields (typedef struct {unsigned char R, G, B;} pixel) in a function foo into a new 24-bit pointer.
```cpp
typedef struct {
    unsigned char R, G, B;
} pixel;
pixel AB;
#pragma HLS data_pack variable=AB
```

3. The DATA_PACK compilation directive is applied to input and output parameters of the rgb_to_hsv function, indicating to the compiler to pack structures on an 8-bit boundary to improve memory access.
```cpp
void rgb_to_hsv(
    RGBcolor* in, // Access global memory as RGBcolor structwise 
    HSVcolor* out, // Access Global Memory as HSVcolor structwise 
    int size) { 
    #pragma HLS data_pack variable=in struct_level 
    #pragma HLS data_pack variable=out struct_level ...
}
```
"""

# select suitable opt option from the pragma list
OPT_CHOICE_PROMPT = \
"""
In HLS(high-level-synthesis), code optimization can be achieved by adding various types of compilation directive (pragmas). Different pragmas are suitable for different scenarios and cannot be applied arbitrarily. The following are some function introductions and applicable scenarios of pragmas: 
{PRAGMA_DESCRIPTION}
The following code is one stage of the algorithm. Please determine which kind of optimizations can be applied to this stage. You can choose some optimization options that are most suitable for applying to this stage of code from the following optimization options
{STAGE_CODE_CONTENT}
Note that not all optimization options are suitable for this stage. 
You only need to select the suitable optimization options, without providing the optimized code. 
Please return the answer in the following format without any explaination: [option_1, option_2, ..., option_n]
If the code no longer needs optimization, you can return null.
"""

# apply optimization to the stage code according to the opt list
APPLY_OPT_PROMPT = \
"""
In HLS(high-level-synthesis), code optimization can be achieved by adding various types of compilation directive (pragmas). The following code is one stage of the whole algorithm: 
{STAGE_CODE_CONTENT}
Please apply the following optimization pragma to the above code: 
{OPT_LIST}
The parameter descriptions and usage examples of these pragmas are as follows: 
{PRAGMA_DEMO}
Please apply these pragmas in appropriate places based on parameter descriptions and reference examples.
Note that you only need to return the optimized code without any explaination. 
"""

OPT_EXPERIENCE_EXTRACT_PROMPT = \
f"""
The following code is the hardware implementation of {REF_OPT_ALGO}, which is fully optimized by the hardware designer. 
"""
