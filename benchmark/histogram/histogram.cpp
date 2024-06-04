#include "histogram.h"

void histogram(int in[INPUT_SIZE], int hist[VALUE_SIZE]) {
    int val;
    for (int i = 0; i < INPUT_SIZE; i++) {
        val = in[i];
        hist[val] = hist[val] + 1;
    }
}