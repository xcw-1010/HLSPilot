#include "insert_sort.h"

void insert_sort(DTYPE A[SIZE]) {
L1: 
    for (int i = 1; i < SIZE; i++) {
        DTYPE item = A[i];
        int j = i;
        DTYPE t = A[j - 1];
    L2:
        while (j - 1 > 0 && A[j - 1] > item) {
            A[j] = A[j - 1];
            j--;
        }
        A[j] = item;
    }

}