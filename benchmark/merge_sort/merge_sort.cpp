#include "merge_sort.h"
#include "assert.h"

// subarray1 is in[i1..i2-1], subarray2 is in[i2..i3-1], result is in out[i1..i3-1]
void merge(DTYPE in[SIZE], int i1, int i2, int i3, DTYPE out[SIZE]) {
    int f1 = i1, f2 = i2;
    for (int idx = i1; idx < i3; idx++) {
        if ((f1 < f2 && in[f1] <= in[f2]) || f2 == i3) {
            out[idx] = in[f1++];
        } else {
            assert(f2 < i3);
            out[idx] = in[f2++];
        }
    }
}

void merge_sort(DTYPE A[SIZE]) {
    DTYPE temp[SIZE];

stage:
    for (int width = 1; width < SIZE; width = 2 * width) {
    merge_arrays:
        for (int i1 = 0; i1 < SIZE; i1 = i1 + 2 * width) {
            int i2 = i1 + width;
            int i3 = i1 + 2 * width;
            if (i2 >= SIZE) i2 = SIZE;
            if (i3 >= SIZE) i3 = SIZE;
            merge(A, i1, i2, i3, temp);
        }

    copy:
        for (int i = 0; i < SIZE; i++) {
            A[i] = temp[i];
        }
    }


}