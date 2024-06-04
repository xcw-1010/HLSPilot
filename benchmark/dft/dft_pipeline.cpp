#include <math.h>
#include <hls_stream.h>

typedef double IN_TYPE;
typedef double TEMP_TYPE;

#define N 256

void dft_stage1(IN_TYPE sample_real[N], IN_TYPE sample_imag[N], hls::stream<TEMP_TYPE>& real_stream, hls::stream<TEMP_TYPE>& imag_stream) {
    for (int i = 0; i < N; i++) {
        real_stream << 0;
        imag_stream << 0;
    }
}

void dft_stage2(IN_TYPE sample_real[N], IN_TYPE sample_imag[N], hls::stream<TEMP_TYPE>& real_stream, hls::stream<TEMP_TYPE>& imag_stream) {
    

}


/*
bfs:
stage1: load rpao to stream if active
stage2: read and traverse ngb of rpao stream
*/