#include "prefix_sum.h"

void prefix_sum(int in[SIZE], int out[SIZE]) {
    out[0] = in[0];
    for (int i = 1; i < SIZE; i++) {
        out[i] = out[i - 1] + in[1];
    }
}

void prefix_sum_opt(int in[SIZE], int out[SIZE]) {
    int A = in[0];
    for (int i = 0; i < SIZE; i++) {
        A = A + in[i];
        out[i] = A;
    }
}