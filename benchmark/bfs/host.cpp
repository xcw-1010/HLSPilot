#include "xcl.h"
#include "graph.h"

#include <cstdio>
#include <vector>
#include <ctime>

Graph* createGraph(const std::string &gName) {
    Graph* gptr;
    std::string dataDir = "./";
    std::string dataPath = dataDir + gName + ".txt";
    gptr = new Graph(dataPath);
    return gptr;
}

int align(int num, int dataWidth, int alignedWidth) {
    if (dataWidth > alignedWidth) {
        std::cout << "Aligning to smaller data width is not supported." << std::endl;
        return -1;
    }
    int wordNum = alignedWidth / dataWidth;
    int alignedNum = ((num - 1) / wordNum + 1) * wordNum;
    return alignedNum;
}

void init(int vertexNum, char* depth, int startVertexIdx) {
    for (int i = 0; i < vertexNum; i++) {
        depth[i] = -1;
    }
    depth[startVertexIdx] = 0;
}

int main(int argc, char **argv) {
    std::clock_t start;
    std::clock_t end;
    double elapsedTime;

    int startVertexIdx = 12345;

    // load graph
    std::string gName = "rmat-21-32";
    Graph* gptr = createGraph(gName);
    CSR* csr = new CSR(*gptr);
    int vertexNum = align(csr->vertexNum, 8, 512);
    free(gptr);
    std::cout << "Graph " << gName << " is loaded." << std::endl;
    std::cout << "VertexNum " << csr->vertexNum << " is aligned to " << vertexNum << std::endl;
    
    // bfs init
    char *hwDepth = (char*)malloc(vertexNum * sizeof(char));
    int frontierSize = 1;
    int ciaoSize = csr->ciao.size();
    int rpaoSize = csr->rpao.size();
    init(vertexNum, hwDepth, startVertexIdx);

    xcl_world world = xcl_world_single();
    cl_program program = xcl_import_binary(world, "bfs.hw");
    cl_kernel krnl_bfs = xcl_get_kernel(program, "bfs");

    cl_mem devMemRpao = xcl_malloc(world, CL_MEM_READ_ONLY, rpaoSize * sizeof(int));
    cl_mem devMemCiao = xcl_malloc(world, CL_MEM_READ_ONLY, ciaoSize * sizeof(int));
    cl_mem devMemDepth = xcl_malloc(world, CL_MEM_READ_WRITE, vertexNum * sizeof(char));
    cl_mem devMemFrontierSize = xcl_malloc(world, CL_MEM_WRITE_ONLY, sizeof(int));

    xcl_memcpy_to_device(world, devMemRpao, csr->rpao.data(), rpaoSize * sizeof(int));
    xcl_memcpy_to_device(world, devMemCiao, csr->ciao.data(), ciaoSize * sizeof(int));
    xcl_memcpy_to_device(world, devMemDepth, hwDepth, vertexNum * sizeof(char));

    int nargs = 0;
    xcl_set_kernel_arg(krnl_bfs, nargs++, sizeof(cl_mem), &devMemDepth);
    xcl_set_kernel_arg(krnl_bfs, nargs++, sizeof(cl_mem), &devMemRpao);
    xcl_set_kernel_arg(krnl_bfs, nargs++, sizeof(cl_mem), &devMemCiao);
    xcl_set_kernel_arg(krnl_bfs, nargs++, sizeof(cl_mem), &devMemFrontierSize);
    xcl_set_kernel_arg(krnl_bfs, nargs++, sizeof(cl_mem), &vertexNum);
    

    char level = 0;
    start = clock();
    while (frontierSize != 0) {
        xcl_set_kernel_arg(krnl_bfs, nargs, sizeof(char), &level);
        xcl_run_kernel3d(world, krnl_bfs, 1, 1, 1);
        xcl_memcpy_from_device(world, &frontierSize, devMemFrontierSize, sizeof(int));
    }
    end = clock();


    clFinish(world.command_queue);
    xcl_memcpy_from_device(world, hwDepth, devMemDepth, vertexNum * sizeof(char));

    elapsedTime = (end - start) * 1.0 / CLOCKS_PER_SEC;
    std::cout << "Elapse time = " << elapsedTime << " seconds." << std::endl;
    std::cout << "Level = " << (int)level << std::endl;

    clReleaseMemObject(devMemRpao);
	clReleaseMemObject(devMemCiao);
	clReleaseMemObject(devMemDepth);
	clReleaseMemObject(devMemFrontierSize);
	clReleaseKernel(krnl_bfs);
	clReleaseProgram(program);
	xcl_release_world(world);

    free(csr);
    free(hwDepth);

    return 0;
}