ROOT_REPO = /home/xiongchengwei/project/rosetta-benchmark/3d-rendering

# Set compiler
CC		= g++
CFLAGS	= -std=c++11 -Wall -g -o0
XOCC        = v++
XOCC_FLAGS  = -t hw --config ${ROOT_REPO}/design.cfg -c

# Set kernel name
KERNEL_NAME = rendering

# Set host source and headers
HOST_SRC_CPP = ${ROOT_REPO}/src/host/3d_rendering_host.cpp ${ROOT_REPO}/src/host/utils.cpp ${ROOT_REPO}/src/host/check_result.cpp ${ROOT_REPO}/../utils/xcl.c
HOST_SRC_H   = ${ROOT_REPO}/src/host/utils.h ${ROOT_REPO}/src/host/check_result.h ${ROOT_REPO}/src/host/typedefs.h ${ROOT_REPO}/src/host/input_data.h 
DATA         = 

# Set host code include paths
HOST_INC = -I$(XILINX_VIVADO)/include/ -I${XILINX_XRT}/include/
HOST_LIB = -L$(XILINX_XRT)/lib
HOST_LDFLAGS = -lOpenCL -lpthread -lrt -lstdc++

# Set kernel file
KERNEL_INC = -I${ROOT_REPO}/src/
KERNEL_SRC = ${ROOT_REPO}/src/sdsoc/${KERNEL_NAME}.cpp
KERNEL_H = ${ROOT_REPO}/src/host/typedefs.h
OBJS  = ${ROOT_REPO}/build/${KERNEL_NAME}.hw.xo

SW_KERNEL_SRC = ${ROOT_REPO}/src/sw/rendering_sw.cpp
SW_KERNEL_H = ${ROOT_REPO}/src/host/typedefs.h ./src/sw/rendering_sw.h

TARGET   = $(ROOT_REPO)/build/3d_rendering_host


all:
	$(CC) $(HOST_INC) $(CFLAGS) $(HOST_SRC_CPP) -o $(TARGET) $(HOST_LIB) $(HOST_LDFLAGS)
#	${XOCC} ${XOCC_FLAGS} -k ${KERNEL_NAME} ${KERNEL_INC} -o${OBJS} ${KERNEL_SRC}

# v++ -t hw --config design.cfg -l -o'bfs.hw.xclbin' bfs.hw.xo
