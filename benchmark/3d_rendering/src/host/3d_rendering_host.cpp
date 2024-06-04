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
    printf("3D Rendering Application\n");
    // for this benchmark, data is included in array triangle_3ds

    // timers
    struct timeval start, end;

    // create xcl world and kernel
    xcl_world world = xcl_world_single();
    cl_program program = xcl_import_binary_file(world, "rendering.hw.xclbin");
    cl_kernel krnl_rendering = xcl_get_kernel(program, "rendering");

    // create space for input and output
    bit32* input = new bit32[3 * NUM_3D_TRI];
    bit32* output = new bit32[NUM_FB];
    for (int i = 0; i < NUM_3D_TRI; i++) {
        input[3 * i](7, 0)       = triangle_3ds[i].x0;
        input[3 * i](15, 8)      = triangle_3ds[i].y0;
        input[3 * i](23, 16)     = triangle_3ds[i].z0;
        input[3 * i](31, 24)     = triangle_3ds[i].x1;
        input[3 * i + 1](7, 0)   = triangle_3ds[i].y1;
        input[3 * i + 1](15, 8)  = triangle_3ds[i].z1;
        input[3 * i + 1](23, 16) = triangle_3ds[i].x2;
        input[3 * i + 1](31, 24) = triangle_3ds[i].y2;
        input[3 * i + 2](7, 0)   = triangle_3ds[i].z2;
        input[3 * i + 2](31, 8)  = 0;
    }


    // create mem object and copy mem to device
    cl_mem devMemInput = xcl_malloc(world, CL_MEM_READ_ONLY, 3 * NUM_3D_TRI * sizeof(bit32));
    cl_mem devMemOutput = xcl_malloc(world, CL_MEM_WRITE_ONLY, NUM_FB * sizeof(bit32));

    xcl_memcpy_to_device(world, devMemInput, input, 3 * NUM_3D_TRI * sizeof(bit32));

    // set kernel args
    int nargs = 0;
    xcl_set_kernel_arg(krnl_rendering, nargs++, sizeof(cl_mem), &devMemInput);
    xcl_set_kernel_arg(krnl_rendering, nargs++, sizeof(cl_mem), &devMemOutput);
    
    // run kernel
    gettimeofday(&start, 0);
    xcl_run_kernel3d(world, krnl_rendering, 1, 1, 1);
    gettimeofday(&end, 0);

    // transfer output data to host
    clFinish(world.command_queue);
    xcl_memcpy_from_device(world, output, devMemOutput, NUM_FB * sizeof(bit32));

 
    // check results
    printf("Checking results:\n");
    check_results(output);
    
    // print time
    long long elapsed = (end.tv_sec - start.tv_sec) * 1000000LL + end.tv_usec - start.tv_usec;   
    printf("elapsed time: %lld us\n", elapsed);

    // cleanup
    clReleaseMemObject(devMemInput);
    clReleaseMemObject(devMemOutput);
    clReleaseKernel(krnl_rendering);
    clReleaseProgram(program);
    xcl_release_world(world);
    

    return EXIT_SUCCESS;
}
