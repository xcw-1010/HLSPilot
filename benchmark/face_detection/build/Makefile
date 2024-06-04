######################## host ########################
# Set Compilers
CXX = g++

ROOT_REPO = /home/xiongchengwei/project/rosetta-benchmark/face_detection

KERNEL_NAME = face_detect

# Set host source and headers
HOST_SRC_CPP = ${ROOT_REPO}/src/host/face_detect_host.cpp \
               ${ROOT_REPO}/src/host/utils.cpp \
			   ${ROOT_REPO}/src/host/check_result.cpp \
			   ${ROOT_REPO}/src/host/image.cpp
HOST_SRC_H	 = ${ROOT_REPO}/src/host/utils.h \
               ${ROOT_REPO}/src/host/check_result.h \
			   ${ROOT_REPO}/src/host/image0_320_240.h \
			   ${ROOT_REPO}/src/host/typedefs.h \
			   ${ROOT_REPO}/src/host/image.h
XCL_UTIL_CPP = ${ROOT_REPO}/../utils/xcl.c
XCL_UTIL_H   = ${ROOT_REPO}/../utils/xcl.h

# Set host code include paths
HOST_INC = -I$(XILINX_VIVADO)/include/ \
           -I${XILINX_XRT}/include/ \
		   -I${ROOT_REPO}/../utils
HOST_LIB = -L${XILINX_VIVADO}/lib \
           -L$(XILINX_XRT)/lib

# Set host compilation flags
VITIS_HOST_FLAGS = -std=c++11 -Wall -g -o0 ${HOST_INC} ${HOST_LIB}
VITIS_HOST_LDFLAGS = -lOpenCL -lpthread -lrt -lstdc++


# vitis host executable file
VITIS_HOST = ${KERNEL_NAME}_host

host: ${VITIS_HOST}
${VITIS_HOST}: ${HOST_SRC_CPP} ${HOST_SRC_H} ${XCL_UTIL_CPP} ${XCL_UTIL_H} ${DATA}
	${CXX} ${VITIS_HOST_FLAGS} -o $@ ${HOST_SRC_CPP} ${XCL_UTIL_CPP} ${VITIS_HOST_LDFLAGS}

######################## kernel ########################
# Set compilers
XOCC       = v++
XOCC_FLAGS = -t hw --config ${ROOT_REPO}/build/design.cfg

# Set kernel file
KERNEL_SRC = ${ROOT_REPO}/src/sdsoc/face_detect.cpp
KERNEL_H   = ${ROOT_REPO}/src/host/typedefs.h \
             ${ROOT_REPO}/src/sdsoc/*.h

XCLBIN = ${KERNEL_NAME}.hw.xclbin
XO     = ${KERNEL_NAME}.hw.xo

xclbin: ${XO}
${XCLBIN}: ${XO}
	${XOCC} -l ${XOCC_FLAGS} -o $@ ${XO}

${XO}: ${KERNEL_SRC} ${KERNEL_H}
	${XOCC} -c ${XOCC_FLAGS} -k ${KERNEL_NAME} -o $@ ${KERNEL_SRC}


# ROOT_REPO = /home/xiongchengwei/project/rosetta-benchmark/face_detection

# # Set compiler
# CC		= g++
# CFLAGS	= -std=c++11 -Wall -g -o0
# XOCC        = v++
# XOCC_FLAGS  = -t hw --config ${ROOT_REPO}/build/design.cfg -c

# # Set kernel name
# KERNEL_NAME = face_detect

# # Set host source and headers
# HOST_SRC_CPP = ${ROOT_REPO}/src/host/face_detect_host.cpp ${ROOT_REPO}/src/host/image.cpp ${ROOT_REPO}/src/host/utils.cpp ${ROOT_REPO}/src/host/check_result.cpp ${ROOT_REPO}/../utils/xcl.c
# HOST_SRC_H   = ${ROOT_REPO}/src/host/utils.h ${ROOT_REPO}/src/host/check_result.h ${ROOT_REPO}/src/host/typedefs.h
# DATA         = 

# # Set host code include paths
# HOST_INC = -I$(XILINX_VIVADO)/include/ -I${XILINX_XRT}/include/
# HOST_LIB = -L$(XILINX_XRT)/lib
# HOST_LDFLAGS = -lOpenCL -lpthread -lrt -lstdc++

# # Set kernel file
# KERNEL_INC = -I${ROOT_REPO}/src/
# KERNEL_SRC = ${ROOT_REPO}/src/sdsoc/face_detect.cpp
# KERNEL_H = ${ROOT_REPO}/src/host/typedefs.h
# OBJS  = ${ROOT_REPO}/build/face_detect.hw.xo

# TARGET   = $(ROOT_REPO)/build/face_detect_host


# all:
# 	$(CC) $(HOST_INC) $(CFLAGS) $(HOST_SRC_CPP) -o $(TARGET) $(HOST_LIB) $(HOST_LDFLAGS)
# 	${XOCC} ${XOCC_FLAGS} -k ${KERNEL_NAME} ${KERNEL_INC} -o${OBJS} ${KERNEL_SRC}

# v++ -t hw --config design.cfg -l -o'face_detect.hw.xclbin' face_detect.hw.xo
