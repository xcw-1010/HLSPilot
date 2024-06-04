static void cc_kernel(
    const int *rpao, 
    const int *ciao, 
    int       *labels, 
    const int vertex_num
) {
    int cur_label = 0;

    for (int i = 0; i < vertex_num; i++) {
        if (labels[i] == -1) {
            int front = 0;
            int rear = 0;
            int *queue = new int[vertex_num];

            queue[rear++] = i;
            labels[i] = cur_label;

            while (front < rear) {
                int cur_idx = queue[front++];

                int start = rpao[cur_idx];
                int end = rpao[cur_idx + 1];

                for (int j = start; j < end; j++) {
                    int ngb_idx = ciao[j];
                    if (labels[ngb_idx] == -1) {
                        labels[ngb_idx] = cur_idx;

                        queue[rear++] = ngb_idx;
                    }
                }
            }
        }
        cur_label++;
    }
}

extern "C" {
    void bfs(
        const int *rpao, 
        const int *ciao, 
        int       *labels, 
        const int vertex_num
    ) {
#pragma HLS INTERFACE m_axi port=rpao offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=ciao offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=labels offset=slave bundle=gmem2

#pragma HLS INTERFACE s_axilite port=vertex_num bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

        cc_kernel(rpao, ciao, labels, vertex_num);
    }
}