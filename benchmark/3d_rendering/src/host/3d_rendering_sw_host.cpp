/*===============================================================*/
/*                                                               */
/*                       3d_rendering.cpp                        */
/*                                                               */
/*      Main host function for the 3D Rendering application.     */
/*                                                               */
/*===============================================================*/

// standard C/C++ headers
#include <cstdio>
#include <cstdlib>
#include <getopt.h>
#include <string>
#include <time.h>
#include <sys/time.h>

#include "../../../utils/xcl.h"

// other headers
#include "utils.h"
#include "typedefs.h"
#include "check_result.h"

// data
#include "input_data.h"


int main(int argc, char ** argv) 
{
    printf("3D Rendering Application (Initial Edition)\n");
    // for this benchmark, data is included in array triangle_3ds

    // timers
    struct timeval start, end;

    // create xcl world and kernel
    xcl_world world = xcl_world_single();
    cl_program program = xcl_import_binary_file(world, "rendering_sw.hw.xclbin");
    cl_kernel krnl_rendering = xcl_get_kernel(program, "rendering_sw");

    // sw: void rendering_sw( Triangle_3D triangle_3ds[NUM_3D_TRI], bit8 output[MAX_X][MAX_Y])
    // opt: void rendering( bit32 input[3*NUM_3D_TRI], bit32 output[NUM_FB])
    bit8 output[MAX_X][MAX_Y];

    // create mem object and copy mem to device
    cl_mem devMemTriangles = xcl_malloc(world, CL_MEM_READ_ONLY, NUM_3D_TRI * sizeof(Triangle_3D));
    cl_mem devMemOutput = xcl_malloc(world, CL_MEM_WRITE_ONLY, MAX_X * MAX_Y * sizeof(bit8));


    xcl_memcpy_to_device(world, devMemTriangles, triangle_3ds, NUM_3D_TRI * sizeof(Triangle_3D));

    // set kernel args
    int nargs = 0;
    xcl_set_kernel_arg(krnl_rendering, nargs++, sizeof(cl_mem), &devMemTriangles);
    xcl_set_kernel_arg(krnl_rendering, nargs++, sizeof(cl_mem), &devMemOutput);
    
    // run kernel
    gettimeofday(&start, 0);
    xcl_run_kernel3d(world, krnl_rendering, 1, 1, 1);
    gettimeofday(&end, 0);

    // transfer output data to host
    clFinish(world.command_queue);
    xcl_memcpy_from_device(world, output, devMemOutput, MAX_X * MAX_Y * sizeof(bit8));

 
    // check results
    printf("Checking results:\n");
    check_results_sw(output);
    
    // print time
    long long elapsed = (end.tv_sec - start.tv_sec) * 1000000LL + end.tv_usec - start.tv_usec;   
    printf("elapsed time: %lld us\n", elapsed);

    // cleanup
    clReleaseMemObject(devMemTriangles);
    clReleaseMemObject(devMemOutput);
    clReleaseKernel(krnl_rendering);
    clReleaseProgram(program);
    xcl_release_world(world);
    

    return EXIT_SUCCESS;
}
