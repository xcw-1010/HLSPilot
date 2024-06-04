#include "fir.h"

void fir(int input, int *output, int taps[NUM_TAPS]) {
    static int delay_lane[NUM_TAPS] = {};

    int result = 0;
    for (int i = NUM_TAPS - 1; i > 0; i--) {
        delay_lane[i] = delay_lane[i - 1];
    }
    delay_lane[0] = input;

    for (int i = 0; i < NUM_TAPS; i++) {
        result += delay_lane[i] * taps[i];
    }

    *output = result;
}