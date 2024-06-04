/*===============================================================*/
/*                                                               */
/*                       face_detect.cpp                         */
/*                                                               */
/*     Main host function for the Face Detection application.    */
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
#include "image0_320_240.h"

int main(int argc, char ** argv) 
{
    printf("Face Detection Application (Initial Edition)\n");

    std::string outFile("./output.pgm");

    // timers
    struct timeval start, end;

    // vitis version host code
    // create xcl world and kernel
    xcl_world world = xcl_world_single();
    cl_program program = xcl_import_binary_file(world, "face_detect_sw.hw.xclbin");
    cl_kernel krnl_face_detect = xcl_get_kernel(program, "face_detect_sw");

    // create space for input and output data
    // for this benchmark, input data is included in array Data
    // these are outputs
    int result_x[RESULT_SIZE];
    int result_y[RESULT_SIZE];
    int result_w[RESULT_SIZE];
    int result_h[RESULT_SIZE];
    int res_size = 0;
    
    // create mem object and copy mem to device
    cl_mem devMemInData = xcl_malloc(world, CL_MEM_READ_ONLY, IMAGE_HEIGHT * IMAGE_WIDTH * sizeof(unsigned char));
    cl_mem devMemResultX = xcl_malloc(world, CL_MEM_WRITE_ONLY, RESULT_SIZE * sizeof(int));
    cl_mem devMemResultY = xcl_malloc(world, CL_MEM_WRITE_ONLY, RESULT_SIZE * sizeof(int));
    cl_mem devMemResultW = xcl_malloc(world, CL_MEM_WRITE_ONLY, RESULT_SIZE * sizeof(int));
    cl_mem devMemResultH = xcl_malloc(world, CL_MEM_WRITE_ONLY, RESULT_SIZE * sizeof(int));
    cl_mem devMemResSize = xcl_malloc(world, CL_MEM_WRITE_ONLY, sizeof(int));

    // copy mem, set kernel args, run kernel
    gettimeofday(&start, 0);
    xcl_memcpy_to_device(world, devMemInData, Data, IMAGE_HEIGHT * IMAGE_WIDTH * sizeof(unsigned char));
    xcl_set_kernel_arg(krnl_face_detect, 0, sizeof(cl_mem), &devMemInData);
    xcl_set_kernel_arg(krnl_face_detect, 1, sizeof(cl_mem), &devMemResultX);
    xcl_set_kernel_arg(krnl_face_detect, 2, sizeof(cl_mem), &devMemResultY);
    xcl_set_kernel_arg(krnl_face_detect, 3, sizeof(cl_mem), &devMemResultW);
    xcl_set_kernel_arg(krnl_face_detect, 4, sizeof(cl_mem), &devMemResultH);
    xcl_set_kernel_arg(krnl_face_detect, 5, sizeof(cl_mem), &devMemResSize);
    xcl_run_kernel3d(world, krnl_face_detect, 1, 1, 1);
    gettimeofday(&end, 0);
    
    // check results
    printf("Checking results:\n");
    check_results(res_size, result_x, result_y, result_w, result_h, Data, outFile);
        
    // print time
    long long elapsed = (end.tv_sec - start.tv_sec) * 1000000LL + end.tv_usec - start.tv_usec;   
    printf("elapsed time: %lld us\n", elapsed);

    // cleanup
    clReleaseMemObject(devMemInData);
    clReleaseMemObject(devMemResultX);
    clReleaseMemObject(devMemResultY);
    clReleaseMemObject(devMemResultW);
    clReleaseMemObject(devMemResultH);
    clReleaseKernel(krnl_face_detect);
    clReleaseProgram(program);
    xcl_release_world(world);

    return EXIT_SUCCESS;

}
