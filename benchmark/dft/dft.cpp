#include <math.h>

typedef double IN_TYPE;
typedef double TEMP_TYPE;

#define N 256

void dft(IN_TYPE sample_real[N], IN_TYPE sample_imag[N]) {
    int i, j;
    TEMP_TYPE w;
    TEMP_TYPE c, s;

    TEMP_TYPE temp_real[N];
    TEMP_TYPE temp_imag[N];

    for (int i = 0; i < N; i++) {
        temp_real[i] = 0;
        temp_imag[i] = 0;

        w = (2.0 * 3.141592653589 / N) * (TEMP_TYPE)i;

        for (j = 0; j < N; j++) {
            c = cos(j * w);
            s = sin(j * w);

            temp_real[i] += (sample_real[j] * c - sample_imag[j] * s);
            temp_imag[i] += (sample_real[j] * s - sample_imag[j] * c);
        }
    }

    for (int i = 0; i < N; i++) {
        sample_real[i] = temp_real[i];
        sample_imag[i] = temp_imag[i];
    }
}