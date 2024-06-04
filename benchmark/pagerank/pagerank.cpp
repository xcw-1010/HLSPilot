#include <hls_stream.h>
#include <ap_int.h>
#include <stdio.h>

static void pagerank_kernel(
    const int *rpao, 
    const int *ciao, 
    float *pr, 
    const int vertex_num, 
    const float damping_factor
) {
    float new_pr[vertex_num];
    for (int i = 0; i < vertex_num; i++) {
        int start = rpao[i];
        int end = rpao[i + 1];
        for (int j = start; j < end; j++) {
            int ngb_idx = ciao[j];
            new_pr[ngb_idx] += pr[i] / (end - start);
        }
    }

    for (int i = 0; i < vertex_num; i++) {
        new_pr[i] = (1.0 - damping_factor) / vertex_num + damping_factor * new_pr[i];
    }
}

extern "C" {
    void pagerank(
        const int *rpao, 
        const int *ciao, 
        float *pr, 
        const int vertex_num, 
        const float damping_factor
    ) {

#pragma HLS INTERFACE m_axi port=rpao offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=ciao offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=pr offset=slave bundle=gmem2

#pragma HLS INTERFACE s_axilite port=vertex_num bundle=control
#pragma HLS INTERFACE s_axilite port=damping_factor bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

        pagerank_kernel(rpao, ciao, pr, vertex_num, damping_factor, max_iterations);
    }
}
