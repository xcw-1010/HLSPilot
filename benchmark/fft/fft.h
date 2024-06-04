#ifndef __FFT_H_
#define __FFT_H_

#define FFT_BITS 10			// Number of bits of FFT, i.e., log(1024)
#define SIZE 1024				// SIZE OF FFT
#define SIZE2 SIZE >> 1 // SIZE/2
#define DTYPE int
#define M 4

unsigned int reverse_bits(unsigned int input);

void bit_reverse(DTYPE X_R[SIZE], DTYPE X_I[SIZE]);

void fft(DTYPE X_R[SIZE], DTYPE X_I[SIZE]);

#endif
