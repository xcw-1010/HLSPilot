#include <hls_stream.h>
#include <ap_int.h>
#include <stdio.h>

static void bfs_kernel(
    char        *depth, 
    const int   *rpao, 
    const int   *ciao, 
    int         *frontier_size, 
    int         vertex_num, 
    const char  level, 
    const char  level_plus1
) {
    char d;
    int start, end;
    int ngb_vidx;
    char ngb_depth;
    int counter = 0;
    for (int i = 0; i < vertex_num; i++) {
        d = depth[i];
        if (d == level) {
            counter++;
            start = rpao[i];
            end = rpao[i + 1];
            for (int j = start; j < end; j++) {
                #pragma HLS PIPELINE
                ngb_vidx = ciao[j];
                ngb_depth = depth[ngb_vidx];
                if (ngb_depth == -1) {
                    depth[ngb_vidx] = level_plus1;
                }
            }
        }
    }
    *frontier_size = counter;
}


extern "C" {
    void bfs(
        char        *depth, 
        const int   *rpao, 
        const int   *ciao, 
        int         *frontier_size, 
        const int   vertex_num, 
        const char  level
    ) {
#pragma HLS INTERFACE m_axi port=depth offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=rpao offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=ciao offset=slave bundle=gmem2
#pragma HLS INTERFACE m_axi port=frontier_size offset=slave bundle=gmem3

#pragma HLS INTERFACE s_axilite port=vertex_num bundle=control
#pragma HLS INTERFACE s_axilite port=level bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

        char level_plus1 = level + 1;
        bfs_kernel(depth, rpao, ciao, frontier_size, vertex_num, level, level_plus1);
    }
}
