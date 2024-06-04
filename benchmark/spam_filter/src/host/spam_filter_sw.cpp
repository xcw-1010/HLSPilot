/*===============================================================*/
/*                                                               */
/*                        spam_filter.cpp                        */
/*                                                               */
/*      Main host function for the Spam Filter application.      */
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

int main(int argc, char *argv[]) 
{
    setbuf(stdout, NULL);

    printf("Spam Filter Application (Initial Edition)\n");

    
    std::string path_to_data("../data");

    // void sgd_sw( DataType    data[NUM_FEATURES * NUM_TRAINING],
    //            LabelType   label[NUM_TRAINING],
    //            FeatureType theta[NUM_FEATURES])
    

    // allocate space for software verification
    DataType*    data_points  = new DataType[NUM_FEATURES * NUM_TRAINING];
    LabelType*   labels       = new LabelType  [NUM_TRAINING];
    FeatureType* param_vector = new FeatureType[NUM_FEATURES];

    // read in dataset
    std::string str_points_filepath = path_to_data + "/shuffledfeats.dat";
    std::string str_labels_filepath = path_to_data + "/shuffledlabels.dat";

    FILE* data_file;
    FILE* label_file;

    // load data from data_file
    data_file = fopen(str_points_filepath.c_str(), "r");
    if (!data_file) {
        printf("Failed to open data file %s!\n", str_points_filepath.c_str());
        return EXIT_FAILURE;
    }
    for (int i = 0; i < NUM_FEATURES * NUM_TRAINING; i ++ ) {
        float tmp;
        fscanf(data_file, "%f", &tmp);
        data_points[i] = tmp;
    }
    fclose(data_file);

    label_file = fopen(str_labels_filepath.c_str(), "r");
    if (!label_file) {
        printf("Failed to open label file %s!\n", str_labels_filepath.c_str());
        return EXIT_FAILURE;
    }
    for (int i = 0; i < NUM_TRAINING; i ++ ) {
        int tmp;
        fscanf(label_file, "%d", &tmp);
        labels[i] = tmp;
    }
    fclose(label_file);

    // reset parameter vector
    for (size_t i = 0; i < NUM_FEATURES; i++)
        param_vector[i] = 0;

    // timers
    struct timeval start, end;

    xcl_world world = xcl_world_single();
    cl_program program = xcl_import_binary_file(world, "sgd_sw.hw.xclbin");
    cl_kernel krnl_sgd = xcl_get_kernel(program, "sgd_sw");

    
    // create mem object and copy mem to device
    cl_mem devMemDataPoints = xcl_malloc(world, CL_MEM_READ_ONLY, NUM_FEATURES * NUM_TRAINING * sizeof(DataType));
    cl_mem devMemLables = xcl_malloc(world, CL_MEM_READ_ONLY, NUM_TRAINING * sizeof(LabelType));
    cl_mem devMemParams = xcl_malloc(world, CL_MEM_WRITE_ONLY, NUM_FEATURES * sizeof(FeatureType));

    xcl_memcpy_to_device(world, devMemDataPoints, data_points, NUM_FEATURES * NUM_TRAINING * sizeof(DataType));
    xcl_memcpy_to_device(world, devMemLables, labels, NUM_TRAINING * sizeof(LabelType));

    // set kernel args
    xcl_set_kernel_arg(krnl_sgd, 0, sizeof(cl_mem), &devMemDataPoints);
    xcl_set_kernel_arg(krnl_sgd, 1, sizeof(cl_mem), &devMemLables);
    xcl_set_kernel_arg(krnl_sgd, 2, sizeof(cl_mem), &devMemParams);

    // run the accelerator
    gettimeofday(&start, NULL);
    xcl_run_kernel3d(world, krnl_sgd, 1, 1, 1);
    gettimeofday(&end, NULL);
    
    // transfer result data to host
    xcl_memcpy_from_device(world, param_vector, devMemParams, NUM_FEATURES * sizeof(FeatureType));

    // check results
    printf("Checking results:\n");
    check_results(param_vector, data_points, labels);
        
    // print time
    long long elapsed = (end.tv_sec - start.tv_sec) * 1000000LL + end.tv_usec - start.tv_usec;   
    printf("elapsed time: %lld us\n", elapsed);

    // cleanup
    clReleaseMemObject(devMemDataPoints);
    clReleaseMemObject(devMemLables);
    clReleaseMemObject(devMemParams);
    clReleaseKernel(krnl_sgd);
    clReleaseProgram(program);
    xcl_release_world(world);

    return EXIT_SUCCESS;
}
