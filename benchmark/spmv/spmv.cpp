#include "spmv.h"

void spmv(int rowPtr[NUM_ROWS + 1], int columnIdx[NNZ], 
        DTYPE values[NNZ], DTYPE y[SIZE], DTYPE x[SIZE]) {
L1: for (int i = 0; i < NUM_ROWS; i++) {
        DTYPE y0 = 0;
    L2: for (int k = rowPtr[i]; k < rowPtr[i + 1]; k++) {
            y0 += values[k] * x[columnIdx[k]];
        }
        y[i] = y0;
    }
}

void matrix_vector(DTYPE A[SIZE][SIZE], DTYPE *y, DTYPE *x) {
    for (int i = 0; i < SIZE; i++) {
        DTYPE y0 = 0;
        for (int j = 0; j < SIZE; j++) {
            y0 += A[i][j] * x[j];
        }
        y[i] = y0;
    }
}