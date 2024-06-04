#include "spmv.h"

const static int factor = 7; // unroll factor

void spmv(int rowPtr[NUM_ROWS + 1], int columnIdx[NNZ], 
        DTYPE values[NNZ], DTYPE y[SIZE], DTYPE x[SIZE]) {
L1: for (int i = 0; i < NUM_ROWS; i++) {
        DTYPE y0 = 0;
    L2_1: for (int k = rowPtr[i]; k < rowPtr[i + 1]; k += factor) {
#pragma HLS pipeline II=factor
            DTYPE yt = values[k] * x[columnIdx[k]];
        L2_2: for (int j = 1; j < factor; j++) {
                if (k + j < rowPtr[i + 1]) {
                    yt += values[k + j] * x[columnIdx[k + j]];
                }
                y0 += yt;
            }
        }
        y[i] = y0;
    }

}