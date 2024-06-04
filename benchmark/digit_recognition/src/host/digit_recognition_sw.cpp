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
    printf("Digit Recognition Application (Initial Edition)\n");

    // for this benchmark, data is already included in arrays:
    //   training_data: contains 18000 training samples, with 1800 samples for each digit class
    //   testing_data:  contains 2000 test samples
    //   expected:      contains labels for the test samples

    // timers
    struct timeval start, end;

    // vitis version host code
    // create xcl world and kernel
    xcl_world world = xcl_world_single();
    cl_program program = xcl_import_binary_file(world, "DigitRec_sw.hw.xclbin");
    cl_kernel krnl_recognition = xcl_get_kernel(program, "DigitRec_sw");
    
    // void DigitRec_sw(const DigitType training_set[NUM_TRAINING * DIGIT_WIDTH], const DigitType test_set[NUM_TEST * DIGIT_WIDTH], LabelType results[NUM_TEST]) 
    // void DigitRec(WholeDigitType global_training_set[NUM_TRAINING / 2], WholeDigitType global_test_set[NUM_TEST], LabelType global_results[NUM_TEST], int run) 
    
    LabelType* result = new LabelType[NUM_TEST];

    // creaet mem object and copy mem to device
    cl_mem devMemTrainingData = xcl_malloc(world, CL_MEM_READ_ONLY, NUM_TRAINING * DIGIT_WIDTH * sizeof(DigitType));
    cl_mem devMemTestingData = xcl_malloc(world, CL_MEM_READ_ONLY, NUM_TEST * DIGIT_WIDTH * sizeof(DigitType));
    cl_mem devMemResult = xcl_malloc(world, CL_MEM_WRITE_ONLY, NUM_TEST * sizeof(LabelType));

    xcl_memcpy_to_device(world, devMemTrainingData, training_data, NUM_TRAINING * DIGIT_WIDTH * sizeof(DigitType));
    xcl_memcpy_to_device(world, devMemTestingData, testing_data, NUM_TEST * DIGIT_WIDTH * sizeof(DigitType));

    // set kernel args
    xcl_set_kernel_arg(krnl_recognition, 0, sizeof(cl_mem), &devMemTrainingData);
    xcl_set_kernel_arg(krnl_recognition, 1, sizeof(cl_mem), &devMemTestingData);
    xcl_set_kernel_arg(krnl_recognition, 2, sizeof(cl_mem), &devMemResult);

    // run kernel
    gettimeofday(&start, 0);
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
    clReleaseMemObject(devMemTrainingData);
    clReleaseMemObject(devMemTestingData);
    clReleaseMemObject(devMemResult);
    clReleaseKernel(krnl_recognition);
    clReleaseProgram(program);
    xcl_release_world(world);
    

    return EXIT_SUCCESS;
}
