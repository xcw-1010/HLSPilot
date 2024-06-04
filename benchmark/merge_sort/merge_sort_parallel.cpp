#include "merge_sort.h"

void merge_arrays(DTYPE in[SIZE], int width, DTYPE out[SIZE]) {
    int f1 = 0;
    int f2 = width;
    int i2 = width;
    int i3 = 2 * width;
    if (i2 >= SIZE) i2 = SIZE;
    if (i3 >= SIZE) i3 = SIZE;

merge_arrays:
    for (int i = 0; i < SIZE; i++) {
#pragma HLS pipeline II=1s
        DTYPE t1 = in[f1];
        DTYPE t2 = in[f2];

        if ((f1 < i2 && t1 <= t2) || f2 == i3) {
            out[i] = t1;
            f1++;
        } else {
            out[i] = t2;
            f2++;
        }

        if (f1 == i2 && f2 == i3) {
            f1 = i3;
            i2 += 2 * width;
            i3 += 2 * width;

            if (i2 >= SIZE) i2 = SIZE;
            if (i3 >= SIZE) i3 = SIZE;
            
            f2 = i2;
        }
    }
}

void merge_sort_parallel(DTYPE A[SIZE], DTYPE B[SIZE]) {
#pragma DATAFLOW

    DTYPE temp[STAGES - 1][SIZE];
#pragma HLS array_partition variable=temp complete dim=1
    int width = 1;

    merge_arrays(A, width, temp[0]);
    width *= 2;

    // 每个stage分别merge区间长度为不同width的区间
    // 不必等所有width=1的区间两两merge完才开始merge width=2的区间
    // stage1: width=1
    // stage2: width=2
    // stage3: width=4
    // stage4: width=8
    for (int stage = 1; stage < STAGES - 1; stage++) {
#pragma HLS unroll
        merge_arrays(temp[stage - 1], width, temp[stage]);
        width *= 2;
    }

    merge_arrays(temp[STAGES - 2], width, B);
}