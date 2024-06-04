ROOT_REPO = /home/xiongchengwei/project/rosetta-benchmark/spam_filter

# Set compiler
CC		= g++
CFLAGS	= -std=c++11 -Wall -g -o0
XOCC        = v++
XOCC_FLAGS  = -t hw --config ${ROOT_REPO}/build/design.cfg -c

# Set kernel name
KERNEL_NAME = SgdLR

# Set host source and headers
HOST_SRC_CPP = ${ROOT_REPO}/src/host/spam_filter.cpp ${ROOT_REPO}/src/host/utils.cpp ${ROOT_REPO}/src/host/check_result.cpp ${ROOT_REPO}/../utils/xcl.c
HOST_SRC_H   = ${ROOT_REPO}/src/host/utils.h ${ROOT_REPO}/src/host/check_result.h ${ROOT_REPO}/src/host/typedefs.h
DATA         = 

# Set host code include paths
HOST_INC = -I$(XILINX_VIVADO)/include/ -I${XILINX_XRT}/include/
HOST_LIB = -L$(XILINX_XRT)/lib
HOST_LDFLAGS = -lOpenCL -lpthread -lrt -lstdc++

# Set kernel file
KERNEL_INC = -I${ROOT_REPO}/src/
KERNEL_SRC = ${ROOT_REPO}/src/sdsoc/sgd.cpp
KERNEL_H = ${ROOT_REPO}/src/host/typedefs.h
OBJS  = ${ROOT_REPO}/build/sgd.hw.xo

TARGET   = $(ROOT_REPO)/build/digit_recognition_host


all:
	$(CC) $(HOST_INC) $(CFLAGS) $(HOST_SRC_CPP) -o $(TARGET) $(HOST_LIB) $(HOST_LDFLAGS)
	${XOCC} ${XOCC_FLAGS} -k ${KERNEL_NAME} ${KERNEL_INC} -o${OBJS} ${KERNEL_SRC}

# v++ -t hw --config design.cfg -l -o'sgd.hw.xclbin' sgd.hw.xo
