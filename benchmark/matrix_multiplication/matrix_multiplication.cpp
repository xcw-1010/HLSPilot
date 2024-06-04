#include "matrix_multiplication.h"

void matrix_mul(BaseType A[N][M], BaseType B[M][P], BaseType AB[N][P]) {
    row: for (int i = 0; i < N; i++) {
        col: for (int j = 0; j < P; j++) {
            int ABij = 0;
            product: for (int k = 0; k < M; k++) {
                ABij += A[i][k] * B[k][j];
            }
            AB[i][j] = ABij;
        }
    }
}