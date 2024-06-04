ROOT_REPO = /home/xiongchengwei/project/rosetta-benchmark/optical_flow

# Set compiler
CC		= g++
CFLAGS	= -std=c++11 -Wall -g -o0
XOCC        = v++
XOCC_FLAGS  = -t hw --config ${ROOT_REPO}/build/design.cfg -c

# Set kernel name
KERNEL_NAME = optical_flow

# Set host source and headers
HOST_SRC_CPP = ${ROOT_REPO}/src/host/optical_flow_host.cpp ${ROOT_REPO}/src/host/utils.cpp ${ROOT_REPO}/src/host/check_result.cpp ${ROOT_REPO}/../utils/xcl.c ${ROOT_REPO}/imageLib/Convert.cpp ${ROOT_REPO}/imageLib/Convolve.cpp ${ROOT_REPO}/imageLib/flowIO.cpp ${ROOT_REPO}/imageLib/Image.cpp ${ROOT_REPO}/imageLib/ImageIO.cpp ${ROOT_REPO}/imageLib/RefCntMem.cpp
HOST_SRC_H   = ${ROOT_REPO}/src/host/utils.h ${ROOT_REPO}/src/host/check_result.h ${ROOT_REPO}/src/host/typedefs.h
DATA         = 

# Set host code include paths
HOST_INC = -I$(XILINX_VIVADO)/include/ -I${XILINX_XRT}/include/
HOST_LIB = -L$(XILINX_XRT)/lib/ -L${ROOT_REPO}/imageLib/
HOST_LDFLAGS = -lOpenCL -lpthread -lrt -lstdc++

# Set kernel file
KERNEL_INC = -I${ROOT_REPO}/src/
KERNEL_SRC = ${ROOT_REPO}/src/sdsoc/optical_flow.cpp
KERNEL_H = ${ROOT_REPO}/src/host/typedefs.h
OBJS  = ${ROOT_REPO}/build/optical_flow.hw.xo

TARGET   = $(ROOT_REPO)/build/optical_flow_host


all:
	$(CC) $(HOST_INC) $(CFLAGS) $(HOST_SRC_CPP) -o $(TARGET) $(HOST_LIB) $(HOST_LDFLAGS)
	${XOCC} ${XOCC_FLAGS} -k ${KERNEL_NAME} ${KERNEL_INC} -o${OBJS} ${KERNEL_SRC}

# v++ -t hw --config design.cfg -l -o'optical_flow.hw.xclbin' optical_flow.hw.xo
