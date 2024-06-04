#define N 32
#define M 32
#define P 32

typedef int BaseType;

extern void matrix_mul(BaseType A[N][M], BaseType B[M][P], BaseType AB[N][P]);