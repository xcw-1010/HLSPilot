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

    printf("Spam Filter Application\n");

    // parse command line arguments
    std::string path_to_data("../data");
    // sdaccel version and sdsoc/sw version have different command line options
    // parse_sdsoc_command_line_args(argc, argv, path_to_data);

    // allocate space for software verification
    DataType*    data_points  = new DataType[DATA_SET_SIZE];
    LabelType*   labels       = new LabelType  [NUM_SAMPLES];
    FeatureType* param_vector = new FeatureType[NUM_FEATURES];

    // read in dataset
    std::string str_points_filepath = path_to_data + "/shuffledfeats.dat";
    std::string str_labels_filepath = path_to_data + "/shuffledlabels.dat";

    FILE* data_file;
    FILE* label_file;

    data_file = fopen(str_points_filepath.c_str(), "r");
    if (!data_file) {
        printf("Failed to open data file %s!\n", str_points_filepath.c_str());
        return EXIT_FAILURE;
    }
    for (int i = 0; i < DATA_SET_SIZE; i ++ ) {
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
    for (int i = 0; i < NUM_SAMPLES; i ++ ) {
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
    cl_program program = xcl_import_binary_file(world, "sgd.hw.xclbin");
    cl_kernel krnl_sgd = xcl_get_kernel(program, "sgd");

    // create space for input and output data
    VectorDataType* data_points_for_accel = new VectorDataType[NUM_FEATURES * NUM_TRAINING / D_VECTOR_SIZE];
    VectorLabelType* labels_for_accel = new VectorLabelType[NUM_TRAINING / L_VECTOR_SIZE];
    VectorFeatureType* param_for_accel = new VectorFeatureType[NUM_FEATURES / F_VECTOR_SIZE];

    // re-organize data points for the accelerator
    for (int i = 0; i < NUM_TRAINING * NUM_FEATURES / D_VECTOR_SIZE; i++) {
        for (int j = 0; j < D_VECTOR_SIZE; j++) {
            data_points_for_accel[i].range((j + 1) * DTYPE_TWIDTH - 1, j * DTYPE_TWIDTH) = data_points[i * D_VECTOR_SIZE + j].range(DTYPE_TWIDTH - 1, 0);
        }
    }

    // re-organize label
    for (int i = 0; i < NUM_TRAINING / L_VECTOR_SIZE; i++) {
        for (int j = 0; j < L_VECTOR_SIZE; j++) {
            labels_for_accel[i].range((j + 1) * LTYPE_WIDTH - 1, j * LTYPE_WIDTH) = labels[i * L_VECTOR_SIZE + j].range(LTYPE_WIDTH - 1, 0);
        }
    }

    // re-organize parameter
    for (int i = 0; i < NUM_FEATURES / F_VECTOR_SIZE; i++) {
        for (int j = 0; j < F_VECTOR_SIZE; j++) {
            param_for_accel[i].range((j + 1) * FTYPE_TWIDTH - 1, j * FTYPE_TWIDTH) = param_vector[i * F_VECTOR_SIZE + j].range(FTYPE_TWIDTH - 1, 0);
        }
    }

    // create mem object and copy mem to device
    cl_mem devMemDataPoints = xcl_malloc(world, CL_MEM_READ_ONLY, NUM_FEATURES * NUM_TRAINING / D_VECTOR_SIZE * sizeof(VectorDataType));
    cl_mem devMemLables = xcl_malloc(world, CL_MEM_READ_ONLY, NUM_TRAINING / L_VECTOR_SIZE * sizeof(VectorLabelType));
    cl_mem devMemParams = xcl_malloc(world, CL_MEM_WRITE_ONLY, NUM_FEATURES / F_VECTOR_SIZE * sizeof(VectorFeatureType));

    xcl_memcpy_to_device(world, devMemDataPoints, data_points_for_accel, NUM_FEATURES * NUM_TRAINING / D_VECTOR_SIZE * sizeof(VectorDataType));
    xcl_memcpy_to_device(world, devMemLables, labels_for_accel, NUM_TRAINING / L_VECTOR_SIZE * sizeof(VectorLabelType));

    // set kernel args
    xcl_set_kernel_arg(krnl_sgd, 0, sizeof(cl_mem), &devMemDataPoints);
    xcl_set_kernel_arg(krnl_sgd, 1, sizeof(cl_mem), &devMemLables);
    xcl_set_kernel_arg(krnl_sgd, 2, sizeof(cl_mem), &devMemParams);

    // run the accelerator
    gettimeofday(&start, NULL);
    for (int epoch = 0; epoch < NUM_EPOCHS; epoch++) {
        bool readLabels = (epoch == 0);
        bool writeOutput = (epoch == 4);
        xcl_set_kernel_arg(krnl_sgd, 3, sizeof(bool), &readLabels);
        xcl_set_kernel_arg(krnl_sgd, 4, sizeof(bool), &writeOutput);

        printf("epoch %d...\n", epoch);
        xcl_run_kernel3d(world, krnl_sgd, 1, 1, 1);
    }
    gettimeofday(&end, NULL);
    
    // transfer result data to host
    xcl_memcpy_from_device(world, param_for_accel, devMemParams, NUM_FEATURES / F_VECTOR_SIZE * sizeof(VectorFeatureType));

    // reorganize the parameter vector
    for (int i = 0; i < NUM_FEATURES / F_VECTOR_SIZE; i++) {
        for (int j = 0; j < F_VECTOR_SIZE; j++) {
            param_vector[i * F_VECTOR_SIZE + j].range(FTYPE_TWIDTH - 1, 0) = param_for_accel[i].range((j + 1) * FTYPE_TWIDTH - 1, j * FTYPE_TWIDTH);
        }
    }

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
