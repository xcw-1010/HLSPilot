#define INPUT_SIZE 8
#define VALUE_SIZE 256

extern void histogram(int in[INPUT_SIZE], int hist[VALUE_SIZE]);

extern void histogram_parallel(int in1[INPUT_SIZE/2], int in2[INPUT_SIZE/2], int hist[VALUE_SIZE]);