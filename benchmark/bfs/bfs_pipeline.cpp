#include <hls_stream.h>
#include <ap_int.h>
#include <stdio.h>

typedef ap_uint<1> uint1_dt;
typedef ap_uint<64> int64_dt;

// load depth for inspection
static void bfs_stage0(
    const char *depth_for_inspect, 
    hls::stream<char> &depth_inspect_stream, 
    int vertex_num
) {
    for (int i = 0; i < vertex_num; i++) {
        #pragma HLS pipeline
        depth_inspect_stream << depth_for_inspect[i];
    }
}

// inspect depth for frontier
// after this stage: 
//     frontier_stream contains current active vertices
//     frontier_stream.size = active vertices size
static void bfs_stage1(
    int *frontier_size, 
    hls::stream<char> &depth_inspect_stream, 
    hls::stream<uint1_dt> &inspect_done_stream, 
    hls::stream<int> &frontier_stream, 
    int vertex_num, 
    const_int level
) {
    char d;
    int counter = 0;

    for (int i = 0; i < vertex_num; i++) {
        #pragma HLS pipeline
        d = depth_inspect_stream.read();
        if (d == level) {
            frontier_stream << i;
            counter++;
        }
    }

    inspect_done_stream << 1;
    *frontier_size = counter;
}

// read rpao of the frontier according to frontier_stream
// after this stage: 
//     rpao_stream contains current active vertices rpao
//     rpao_stream[i]: rpitem(rpao info for one vertex)
//     rpao_done_stream: a '1' per iteration
static void bfs_stage2(
    const int *rpao, 
    hls::stream<int> &frontier_stream, 
    hls::stream<uint1_dt> &inspect_done_stream, 
    hls::stream<int64_dt> &rpao_stream, 
    hls::stream<uint1_dt> &rpao_done_stream
) {
    uint1_dt frontier_empty = 0;
    uint1_dt done_empty = 0;
    uint1_dt done = 0;
    int vidx;
    int64_dt rpitem;

    while ((frontier_empty != 1) || (done != 1)) {
        #pragma HLS pipeline
        frontier_empty = frontier_stream.empty();
        done_empty = inspect_done_stream.empty();

        if (frontier_empty != 1) {
            vidx = frontier_stream.read();
            rpitem.range(31, 0) = rpao[vidx];
            rpitem.range(63, 32) = rpao[vidx + 1];
            rpao_stream << rpitem;
        }

        if (done_empty != 1 && frontier_empty == 1) {
            done = inspect_done_stream.read();
        }
    }

    rpao_done_stream << 1;
}

// read ciao according to rpao
static void bfs_stage3(
    const int *ciao, 
    hls::stream<int64_dt> &rpao_stream, 
    hls::stream<uint1_dt> &rpao_done_stream, 
    hls::stream<int> &ciao_stream, 
    hls::stream<uint1_dt> &ciao_done_stream
) {
    uint1_dt rpao_empty = 0;
    uint1_dt done_empty = 0;
    uint1_dt done = 0;
    int start, end;
    int64_dt rpitem;

    while ((rpao_empty != 1) || (done != 1)) {
        rpao_empty = rpao_stream.empty();
        done_empty = rpao_done_stream.empty();

        if (rpao_empty != 1) {
            rpitem = rpao_stream.read();
            start = rpitem.range(31, 0);
            end = rpitem.range(63, 32);
            for (int i = start; i < end; i++) {
                #pragma HLS pipeline
                ciao_stream << ciao[i];
            }
        }

        if (done_empty != 1 && rpao_empty == 1) {
            done = rpao_done_stream.read();
        }
    }

    ciao_done_stream << 1;
}

// process neighbor depth according to ciao_stream
static void bfs_stage4(
    char *depth, 
    hls::stream<int> &ciao_stream, 
    hls::stream<uint1_dt> &ciao_done_stream, 
    const char level_plus1
) {
    int vidx;
    char ngb_depth;

    int done = 0;
    int ciao_empty = 0;
    int done_empty = 0;

    while (ciao_empty != 1 || done != 1) {
        #pragma HLS pipeline
        ciao_empty = ciao_stream.empty();
        done_empty = ciao_done_stream.empty();
        if (ciao_empty != 1) {
            vidx = ciao_stream.read();
            ngb_depth = depth[vidx];
            if (ngb_depth == -1) {
                depth[vidx] = level_plus1;
            }
        }

        if (done_empty != 1 && ciao_empty == 1) {
            done = ciao_done_stream.read();
        }
    }
}


extern "C" {
    void bfs(
        const char *depth_for_inspect, 
        char *depth_for_update, 
        const int *rpao, 
        const int *ciao, 
        int *frontier_size, 
        const int vertex_num, 
        const char level
    ) {
#pragma HLS INTERFACE m_axi port=depth_for_inspect offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=depth_for_update offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=rpao offset=slave bundle=gmem2
#pragma HLS INTERFACE m_axi port=ciao offset=slave bundle=gmem3
#pragma HLS INTERFACE m_axi port=frontier_size offset=slave bundle=gmem4

#pragma HLS INTERFACE s_axilite port=vertex_num bundle=control
#pragma HLS INTERFACE s_axilite port=level bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

        char level_plus1 = level + 1;

        hls::stream<char> depth_inspect_stream;
        hls::stream<uint1_dt> inspect_done_stream;
        hls::stream<int> frontier_stream;
        hls::stream<int64_dt> rpao_stream;
        hls::stream<uint1_dt> rpao_done_stream;
        hls::stream<int> ciao_stream;
        hls::stream<uint1_dt> ciao_done_stream;

#pragma HLS stream variable=depth_inspect_stream depth=32
#pragma HLS stream variable=frontier_stream depth=32
#pragma HLS stream variable=inspect_done_stream depth=4
#pragma HLS stream variable=rpao_done_stream depth=4
#pragma HLS stream variable=rpao_stream depth=32
#pragma HLS stream variable=ciao_stream depth=32
#pragma HLS stream variable=ciao_done_stream depth=4


#pragma HLS DATAFLOW
        bfs_stage0(depth_for_inspect, depth_inspect_stream, vertex_num);
        bfs_stage1(frontier_size, depth_inspect_stream, inspect_done_stream, frontier_stream, vertex_num, level);
        bfs_stage2(rpao, frontier_stream, inspect_done_stream, rpao_stream, rpao_done_stream);
        bfs_stage3(ciao, rpao_stream, rpao_done_stream, ciao_stream, ciao_done_stream);
        bfs_stage4(depth_for_update, ciao_stream, ciao_done_stream, level_plus1);
    }
}