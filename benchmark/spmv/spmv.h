#ifndef __SPMV_H_
#define __SPMV_H_

const static int SIZE = 4;  // size of square matrix
const static int NNZ = 9;   // number of none-zero elem
const static int NUM_ROWS = 4;  // size
typedef float DTYPE;
void spmv(int rowPtr[NUM_ROWS + 1], int columnIdx[NNZ], DTYPE values[NNZ], DTYPE y[SIZE], DTYPE x[SIZE]);

#endif