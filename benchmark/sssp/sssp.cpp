#include <iostream>

static void sssp_kernel(
    const int *rpao, 
    const int *ciao, 
    const int *weights, 
    int *distance, 
    const int vertex_num, 
    const int src
) {
    for (int i = 0; i < vertex_num; i++) {
        distance[i] = INT_MAX;
    }
    distance[src] = 0;

    bool *visited = new bool[vertex_num]();

    for (int i = 0; i < vertex_num - 1; i++) {
        int min_dis = INT_MAX;
        int min_idx = -1;

        for (int j = 0; j < vertex_num; j++) {
            if (!visited[j] && distance[j] < min_dis) {
                min_dis = distance[j];
                min_idx = j;
            }
        }

        visited[min_idx] = true;

        int start = rpao[min_idx];
        int end = rpao[min_idx + 1];

        for (int j = start; j < end; j++) {
            int ngb_idx = ciao[j];
            int weight = weights[j];
            int new_dis = distance[min_idx] + weight;

            if (new_dis < distance[ngb_idx]) {
                distance[ngb_idx] = new_dis;
            }
        }
    }
}

extern "C" {
    void sssp(
        const int *rpao, 
        const int *ciao, 
        const int *weights, 
        int *distance, 
        const int vertex_num, 
        const int src
    ) {
#pragma HLS INTERFACE m_axi port=rpao offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=ciao offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=weights offset=slave bundle=gmem2
#pragma HLS INTERFACE m_axi port=distance offset=slave bundle=gmem3

#pragma HLS INTERFACE s_axilite port=vertex_num bundle=control
#pragma HLS INTERFACE s_axilite port=src bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

        sssp_kernel(rpao, ciao, weights, distance, vertex_num, src);

    }
}