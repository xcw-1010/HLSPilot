/*===============================================================*/
/*                                                               */
/*                    optical_flow_host.cpp                      */
/*                                                               */
/*      Main host function for the Optical Flow application.     */
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

int main(int argc, char ** argv) 
{
    printf("Optical Flow Application\n");

    // parse command line arguments
    std::string dataPath("../datasets/sintel_alley");
    std::string outFile("./output.flo");

    // create actual file names according to the datapath
    std::string frame_files[5];
    std::string reference_file;
    frame_files[0] = dataPath + "/frame1.ppm";
    frame_files[1] = dataPath + "/frame2.ppm";
    frame_files[2] = dataPath + "/frame3.ppm";
    frame_files[3] = dataPath + "/frame4.ppm";
    frame_files[4] = dataPath + "/frame5.ppm";
    reference_file = dataPath + "/ref.flo";

    // read in images and convert to grayscale
    printf("Reading input files ... \n");

    CByteImage imgs[5];
    for (int i = 0; i < 5; i++) 
    {
        CByteImage tmpImg;
        ReadImage(tmpImg, frame_files[i].c_str());
        imgs[i] = ConvertToGray(tmpImg);
    }

    // read in reference flow file
    printf("Reading reference output flow... \n");

    CFloatImage refFlow;
    ReadFlowFile(refFlow, reference_file.c_str());

    // timers
    struct timeval start, end;

    // vitis version host code
    // create xcl world and kernel
    xcl_world world = xcl_world_single();
    cl_program program = xcl_import_binary_file(world, "optical_flow.hw.xclbin");
    cl_kernel krnl_optical_flow = xcl_get_kernel(program, "optical_flow");

    // create space for input and output data
    static frames_t frames[MAX_HEIGHT][MAX_WIDTH];
    static velocity_t outputs[MAX_HEIGHT][MAX_WIDTH];

    for (int i = 0; i < MAX_HEIGHT; i++) {
        for (int j = 0; j < MAX_WIDTH; j++) {
            frames[i][j](7 ,  0) = imgs[0].Pixel(j, i, 0);
            frames[i][j](15,  8) = imgs[1].Pixel(j, i, 0);
            frames[i][j](23, 16) = imgs[2].Pixel(j, i, 0);
            frames[i][j](31, 24) = imgs[3].Pixel(j, i, 0);
            frames[i][j](39, 32) = imgs[4].Pixel(j, i, 0);
            frames[i][j](63, 40) = 0;
        }
    }

    // create mem object and copy mem to device
    cl_mem devMemFrames = xcl_malloc(world, CL_MEM_READ_ONLY, MAX_HEIGHT * MAX_WIDTH * sizeof(frames_t));
    cl_mem devMemOutputs = xcl_malloc(world, CL_MEM_WRITE_ONLY, MAX_HEIGHT * MAX_WIDTH * sizeof(velocity_t));

    xcl_memcpy_to_device(world, devMemFrames, frames, MAX_HEIGHT * MAX_WIDTH * sizeof(frames_t));
    
    // set kernel args
    xcl_set_kernel_arg(krnl_optical_flow, 0, sizeof(cl_mem), &devMemFrames);
    xcl_set_kernel_arg(krnl_optical_flow, 1, sizeof(cl_mem), &devMemOutputs);

    // run kernel
    printf("Start running kernel...\n");
    gettimeofday(&start, 0);
    xcl_run_kernel3d(world, krnl_optical_flow, 1, 1, 1);
    gettimeofday(&end, 0);

    xcl_memcpy_from_device(world, outputs, devMemOutputs, MAX_HEIGHT * MAX_WIDTH * sizeof(velocity_t));

    // check results
    printf("Checking results:\n");
    check_results(outputs, refFlow, outFile);

    // print time
    long long elapsed = (end.tv_sec - start.tv_sec) * 1000000LL + end.tv_usec - start.tv_usec;   
    printf("elapsed time: %lld us\n", elapsed);

    // cleanup
    clReleaseMemObject(devMemFrames);
    clReleaseMemObject(devMemOutputs);
    clReleaseKernel(krnl_optical_flow);
    clReleaseProgram(program);
    xcl_release_world(world);

    return EXIT_SUCCESS;

}
