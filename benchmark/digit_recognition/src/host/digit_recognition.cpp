/*===============================================================*/
/*                                                               */
/*                    digit_recognition.cpp                      */
/*                                                               */
/*   Main host function for the Digit Recognition application.   */
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
#include "training_data.h"
#include "testing_data.h"

int main(int argc, char ** argv) 
{
    printf("Digit Recognition Application\n");

    // for this benchmark, data is already included in arrays:
    //   training_data: contains 18000 training samples, with 1800 samples for each digit class
    //   testing_data:  contains 2000 test samples
    //   expected:      contains labels for the test samples

    // timers
    struct timeval start, end;

    // vitis version host code
    // create xcl world and kernel
    xcl_world world = xcl_world_single();
    cl_program program = xcl_import_binary_file(world, "digitrec.hw.xclbin");
    cl_kernel krnl_recognition = xcl_get_kernel(program, "DigitRec");

    // create space for input and output data
    WholeDigitType* training_in0 = new WholeDigitType[NUM_TRAINING / 2]; // train0
    WholeDigitType* training_in1 = new WholeDigitType[NUM_TRAINING / 2]; // train1
    WholeDigitType* test_in      = new WholeDigitType[NUM_TEST];         // test
    LabelType*  result           = new LabelType[NUM_TEST];

    for (int i = 0; i < NUM_TRAINING / 2; i++) {
        training_in0[i].range(63, 0)    = training_data[i * DIGIT_WIDTH + 0];
        training_in0[i].range(127, 64)  = training_data[i * DIGIT_WIDTH + 1];
        training_in0[i].range(191, 128) = training_data[i * DIGIT_WIDTH + 2];
        training_in0[i].range(255, 192) = training_data[i * DIGIT_WIDTH + 3];
    }

    for (int i = 0; i < NUM_TRAINING / 2; i++) {
        training_in1[i].range(63, 0)    = training_data[(NUM_TRAINING / 2 + i) * DIGIT_WIDTH + 0];
        training_in1[i].range(127, 64)  = training_data[(NUM_TRAINING / 2 + i) * DIGIT_WIDTH + 1];
        training_in1[i].range(191, 128) = training_data[(NUM_TRAINING / 2 + i) * DIGIT_WIDTH + 2];
        training_in1[i].range(255, 192) = training_data[(NUM_TRAINING / 2 + i) * DIGIT_WIDTH + 3];
    }

    for (int i = 0; i < NUM_TEST; i ++ ) {
        test_in[i].range(63, 0)    = testing_data[i * DIGIT_WIDTH + 0];
        test_in[i].range(127, 64)  = testing_data[i * DIGIT_WIDTH + 1];
        test_in[i].range(191, 128) = testing_data[i * DIGIT_WIDTH + 2];
        test_in[i].range(255, 192) = testing_data[i * DIGIT_WIDTH + 3];
    }

    // creaet mem object and copy mem to device
    cl_mem devMemTrainingIn0 = xcl_malloc(world, CL_MEM_READ_ONLY, (NUM_TRAINING / 2) * sizeof(WholeDigitType));
    cl_mem devMemTrainingIn1 = xcl_malloc(world, CL_MEM_READ_ONLY, (NUM_TRAINING / 2) * sizeof(WholeDigitType));
    cl_mem devMemTestIn = xcl_malloc(world, CL_MEM_READ_ONLY, NUM_TEST * sizeof(WholeDigitType));
    cl_mem devMemResult = xcl_malloc(world, CL_MEM_WRITE_ONLY, NUM_TEST * sizeof(LabelType));

    xcl_memcpy_to_device(world, devMemTrainingIn0, training_in0, (NUM_TRAINING / 2) * sizeof(WholeDigitType));
    xcl_memcpy_to_device(world, devMemTrainingIn1, training_in1, (NUM_TRAINING / 2) * sizeof(WholeDigitType));
    xcl_memcpy_to_device(world, devMemTestIn, test_in, NUM_TEST * sizeof(WholeDigitType));

    int run1 = 0;
    int run1 = 1;

    // set kernel args
    xcl_set_kernel_arg(krnl_recognition, 0, sizeof(cl_mem), &devMemTrainingIn0);
    xcl_set_kernel_arg(krnl_recognition, 1, sizeof(cl_mem), &devMemTestIn);
    xcl_set_kernel_arg(krnl_recognition, 2, sizeof(cl_mem), &devMemResult);
    xcl_set_kernel_arg(krnl_recognition, 3, sizeof(int), &run0);

    // run kernel
    // first call: transfer data
    xcl_run_kernel3d(world, krnl_recognition, 1, 1, 1);

    // second call: execute
    gettimeofday(&start, 0);
    xcl_set_kernel_arg(krnl_recognition, 0, sizeof(cl_mem), &devMemTrainingIn1);
    xcl_set_kernel_arg(krnl_recognition, 1, sizeof(cl_mem), &devMemTestIn);
    xcl_set_kernel_arg(krnl_recognition, 2, sizeof(cl_mem), &devMemResult);
    xcl_set_kernel_arg(krnl_recognition, 3, sizeof(int), &run1);
    xcl_run_kernel3d(world, krnl_recognition, 1, 1, 1);
    gettimeofday(&end, 0);

    // transfer result data to host
    clFinish(world.command_queue);
    xcl_memcpy_from_device(world, result, devMemResult, NUM_TEST * sizeof(LabelType));

    // check results
    printf("Checking results:\n");
    check_results( result, expected, NUM_TEST );
        
    // print time
    long long elapsed = (end.tv_sec - start.tv_sec) * 1000000LL + end.tv_usec - start.tv_usec;   
    printf("elapsed time: %lld us\n", elapsed);

    // cleanup
    clReleaseMemObject(devMemTrainingIn0);
    clReleaseMemObject(devMemTrainingIn1);
    clReleaseMemObject(devMemTestIn);
    clReleaseMemObject(devMemResult);
    clReleaseKernel(krnl_recognition);
    clReleaseProgram(program);
    xcl_release_world(world);
    

    return EXIT_SUCCESS;
}
