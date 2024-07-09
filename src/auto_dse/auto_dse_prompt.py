AUTO_DSE_PROMPT = \
"""
Design space exploration (DSE) is an important step in hardware design. In HLS design, dse is mainly used to explore the performance, power, and resource utilization of designs under different pragma parameters.

There are now many open-source DSE tools that can help automatically explore design spaces. Below, I will provide a user manual for the dse tool. Could you please help generate the necessary inputs for the dse tool.
--------------------------------
User Manual for DSE tool:

HLS Directives DSE based on Genetic Algorithms
In this project we created an optimizer able to automatically perform High-Level Synthesis directives Design Space Exploration leveraging genetic algorithms.

Supported HLS Directives:
    - Loop Pipeline
    - Loop Unroll
    - Array Partition

Optimizer Inputs:
    - synthesizable C/C++ source code annotated with labels in each action point i.e. array, loop (1st action point will be annotated with label L1, 2nd with label L2 etc.)
    - kernel_info.txt that provides a) the top level function name and b) information for each action point. For loop action points users have to provide the loop tripcount and for array action points users have to provide its name as well as the size of each array dimension.

Optimizer Outputs:
    - the Pareto optimal kernel source codes
    - info.csv that describes the Pareto optimal kernel source code tradeoffs
    - a database with the examined directives configurations and their corresponding latencies and resources (BRAM%, DSP%, LUT% and FF%)
    - APP_NAME.json that provides statistics for the database
--------------------------------
To help you generate better results, the following is a corresponding example, which you can refer to as the output result:

----- synthesizable C/C++ source code -------

#include "common.h"
#include "hls_stream.h"

void ReadFromMem(
        unsigned short       width,
        unsigned short       height,
        unsigned short       stride,
        const char          *coeffs,
        hls::stream<char>   &coeff_stream,
        const unsigned char *src,
        hls::stream<U8>     &pixel_stream )
{
    assert(stride <= MAX_IMAGE_WIDTH);
    assert(height <= MAX_IMAGE_HEIGHT);
    assert(stride%64 == 0);

    unsigned num_coefs = 15*15; //FILTER_V_SIZE*FILTER_H_SIZE;
    unsigned num_coefs_padded = (((num_coefs-1)/64)+1)*64; // Make sure number of reads of multiple of 64, enables auto-widening
L1:    read_coefs: for (int i=0; i< 288/*num_coefs_padded*/; i++) {
        U8 coef = coeffs[i];
        if (i<num_coefs) coeff_stream.write( coef );        
    }

    stride = (stride/64)*64; // Makes compiler see that stride is a multiple of 64, enables auto-widening
    unsigned offset = 0;
    unsigned x = 0;
L2:    read_image: for (int n = 0; n < 1920*1080 /*height*stride*/; n++) {
        U8 pix = src[n];
        if (x<width) pixel_stream.write( pix );
        if (x==(stride-1)) x=0; else x++;
     }
}


void WriteToMem(
        unsigned short       width,
        unsigned short       height,
        unsigned short       stride,
        hls::stream<U8>     &pixel_stream,
        unsigned char       *dst)
{
    assert(stride <= MAX_IMAGE_WIDTH);
    assert(height <= MAX_IMAGE_HEIGHT);
    assert(stride%64 == 0);

    stride = (stride/64)*64; // Makes compiler see that stride is a multiple of 64, enables auto-widening
    unsigned offset = 0;
    unsigned x = 0;
L3:    write_image: for (int n = 0; n < 1920*1080/*height*stride*/; n++) {
        U8 pix = (x<width) ? pixel_stream.read() : 0;
        dst[n] = pix;
        if (x==(stride-1)) x=0; else x++;
    }    
}


struct window {
    U8 pix[FILTER_V_SIZE][FILTER_H_SIZE];
};


void Window2D(
        unsigned short        width,
        unsigned short        height,
        hls::stream<U8>      &pixel_stream,
        hls::stream<window>  &window_stream)
{
    // Line buffers - used to store [FILTER_V_SIZE-1] entire lines of pixels
L4:    U8 LineBuffer[FILTER_V_SIZE-1][MAX_IMAGE_WIDTH];  
#pragma HLS DEPENDENCE variable=LineBuffer inter false
#pragma HLS DEPENDENCE variable=LineBuffer intra false

    // Sliding window of [FILTER_V_SIZE][FILTER_H_SIZE] pixels
    window Window;

    unsigned col_ptr = 0;
    unsigned ramp_up = 1920*((FILTER_V_SIZE-1)/2)+(FILTER_H_SIZE-1)/2; //width*((FILTER_V_SIZE-1)/2)+(FILTER_H_SIZE-1)/2;
    unsigned num_pixels = 1920*1080;//width*height;
    unsigned num_iterations = num_pixels + ramp_up;

    const unsigned max_iterations = MAX_IMAGE_WIDTH*MAX_IMAGE_HEIGHT + MAX_IMAGE_WIDTH*((FILTER_V_SIZE-1)/2)+(FILTER_H_SIZE-1)/2;

    // Iterate until all pixels have been processed
L5:    update_window: for (int n=0; n< 2087054/*num_iterations*/; n++)
    {
#pragma HLS LOOP_TRIPCOUNT max=max_iterations

        // Read a new pixel from the input stream
        U8 new_pixel = (n<num_pixels) ? pixel_stream.read() : 0;

        // Shift the window and add a column of new pixels from the line buffer
L6:        for(int i = 0; i < FILTER_V_SIZE; i++) {
L7:            for(int j = 0; j < FILTER_H_SIZE-1; j++) {
                Window.pix[i][j] = Window.pix[i][j+1];
            }
            Window.pix[i][FILTER_H_SIZE-1] = (i<FILTER_V_SIZE-1) ? LineBuffer[i][col_ptr] : new_pixel;
        }

        // Shift pixels in the column of pixels in the line buffer, add the newest pixel
L8:        for(int i = 0; i < FILTER_V_SIZE-2; i++) {
            LineBuffer[i][col_ptr] = LineBuffer[i+1][col_ptr];
        }
        LineBuffer[FILTER_V_SIZE-2][col_ptr] = new_pixel;

        // Update the line buffer column pointer
        if (col_ptr==(width-1)) {
            col_ptr = 0;
        } else {
            col_ptr++;
        }

        // Write output only when enough pixels have been read the buffers and ramped-up
        if (n>=ramp_up) {
            window_stream.write(Window);
        }

    }
}

void Filter2D(
        unsigned short       width,
        unsigned short       height,
        float                factor,
        short                bias,
        hls::stream<char>   &coeff_stream,
        hls::stream<window> &window_stream,
		hls::stream<U8>     &pixel_stream )
{
    assert(width  <= MAX_IMAGE_WIDTH);
    assert(height <= MAX_IMAGE_HEIGHT);

    // Filtering coefficients
L9:    char coeffs[FILTER_V_SIZE][FILTER_H_SIZE];

    // Load the coefficients into local storage
L10:    load_coefs: for (int i=0; i<FILTER_V_SIZE; i++) {
L11:        for (int j=0; j<FILTER_H_SIZE; j++) {
            coeffs[i][j] = coeff_stream.read();
        }
    }

    // Process the incoming stream of pixel windows
L12:    apply_filter: for (int y = 0; y < 1080/*height*/; y++) 
    {
L13:        for (int x = 0; x < 1920/*width*/; x++) 
        {
            // Read a 2D window of pixels
            window w = window_stream.read();

            // Apply filter to the 2D window
            int sum = 0;
L14:            for(int row=0; row<FILTER_V_SIZE; row++) 
            {
L15:                for(int col=0; col<FILTER_H_SIZE; col++) 
                {
                    unsigned char pixel;
                    int xoffset = (x+col-(FILTER_H_SIZE/2));
                    int yoffset = (y+row-(FILTER_V_SIZE/2));
                    // Deal with boundary conditions : clamp pixels to 0 when outside of image 
                    if ( (xoffset<0) || (xoffset>=width) || (yoffset<0) || (yoffset>=height) ) {
                        pixel = 0;
                    } else {
                        pixel = w.pix[row][col];
                    }
                    sum += pixel*(char)coeffs[row][col];
                }
            }

            // Normalize result
            unsigned char outpix = MIN(MAX((int(factor * sum)+bias), 0), 255);

            // Write the output pixel
            pixel_stream.write(outpix);
        }
    }
}


extern "C" {

void Filter2DKernel(
        const char           coeffs[256],
        float                factor,
        short                bias,
        unsigned short       width,
        unsigned short       height,
        unsigned short       stride,
        const unsigned char  src[MAX_IMAGE_WIDTH*MAX_IMAGE_HEIGHT],
        unsigned char        dst[MAX_IMAGE_WIDTH*MAX_IMAGE_HEIGHT])
  {
            
#pragma HLS DATAFLOW

	// Stream of pixels from kernel input to filter, and from filter to output
    hls::stream<char,2>    coefs_stream;
    hls::stream<U8,2>      pixel_stream;
    hls::stream<window,3>  window_stream; // Set FIFO depth to 0 to minimize resources
    hls::stream<U8,64>     output_stream;

	// Read image data from global memory over AXI4 MM, and stream pixels out
    ReadFromMem(width, height, stride, coeffs, coefs_stream, src, pixel_stream);

    // Read incoming pixels and form valid HxV windows
    Window2D(width, height, pixel_stream, window_stream);

	// Process incoming stream of pixels, and stream pixels out
	Filter2D(width, height, factor, bias, coefs_stream, window_stream, output_stream);

	// Write incoming stream of pixels and write them to global memory over AXI4 MM
	WriteToMem(width, height, stride, output_stream, dst);

  }

}

---------- kernel_info.txt -------------
Filter2DKernel
L1,loop,288
L2,loop,2073600
L3,loop,2073600
L4,array,LineBuffer,1,14,2,1920
L5,loop,2087054
L6,loop,15
L7,loop,14
L8,loop,13
L9,array,coeffs,1,15,2,15
L10,loop,15
L11,loop,15
L12,loop,1080
L13,loop,1920
L14,loop,15
L15,loop,15

---------------------------------------------------------

The following is the source code without annotion, please help generate the code annotated with labels in each action point and the kernel_info.txt file:

typedef ap_fixed<96, 72> fixed;

const int basic_depth = 2000;
const int patch_depth = 2000;
const int coeff_depth = basic_depth + patch_depth - 1;

const int max_lm_rank = 5;
const float limit_step = 1;

const fixed lambda = (fixed) 50000;
const fixed cautious_factor = (fixed) 1.0e-6;

const fixed complete_threshold = (fixed) 89000;  	//93994/4.8578


// Stage 1: Compute convolution and cost for each coefficient position
// Each iteration of this loop is independent and could be computed in parallel
void compute_conv_and_cost(
    fixed* basic_memory,
    fixed* coeff_memory,
    fixed* patch_memory,
    fixed* delta_memory,
    int coeff_rank, 
	float* cost
) {
    for(int i = 0; i < (coeff_depth - basic_depth + 1); ++i) {
        // #pragma HLS pipeline
        int is = i + 4000 * coeff_rank;
        fixed conv_ones = 0;
        for(int j = 0; j < basic_depth ; ++j){
            #pragma HLS unroll factor=8
            conv_ones += basic_memory[j] * coeff_memory[is + basic_depth - 1 - j];
        }
        
        fixed deltaValue = patch_memory[i] - conv_ones;
        delta_memory[i] = deltaValue;
    }
	fixed fResidue = 0;
	for (int i = 0; i < (coeff_depth - basic_depth + 1); ++i) {
        #pragma HLS unroll factor=8
		fResidue += delta_memory[i] * delta_memory[i];
	}

	fixed fSparsity = 0;
	for (int i = 0; i < (coeff_depth); ++i) {
        #pragma HLS unroll factor=8
		int is = i + 4000 * coeff_rank;
		fSparsity += lambda * hls::abs(coeff_memory[is]);
	}
	*cost = (float)(fResidue + fSparsity);
}

// Stage 2: Compute gradient for reconstruction error
void compute_gradient(
    fixed* basic_memory,
    fixed* delta_memory,
    fixed* grab_memory, 
    int grab_rank
) {
    for(int j = basic_depth; j > 0 ; --j) {
        // #pragma HLS pipeline
        for(int i = 0; i < patch_depth; ++i) {
			#pragma HLS unroll factor=8
            int grab_addre = i + basic_depth - j + grab_rank * 4000;
            fixed grab_reg = 0;
            if (j == basic_depth) {
				grab_reg = 0;
			} else if(j != basic_depth && i == patch_depth - 1){
				grab_reg = 0;
			} else {
				grab_reg = grab_memory[grab_addre];
			}
            grab_reg += basic_memory[j - 1] * delta_memory[i];
            grab_memory[grab_addre] = grab_reg;
       }
    }
}

// Stage 3: Final gradient calculation and optimization check
void finalize_gradients_and_check_optimization(
    fixed* coeff_memory,
    fixed* grab_memory,
    int coeff_rank, 
    int* opt_complete
) {
    fixed grab_compare = 0;
    fixed coeff_compare = 0;
    for(int i = 0; i < coeff_depth; ++i) {
        #pragma HLS unroll factor=8
        int is = i + coeff_rank * 4000;
        fixed coeff_reg = coeff_memory[is];
        fixed grab_reg = grab_memory[is];
        if (coeff_reg == 0) {
			grab_reg = -2 * grab_reg;
		} else {
			grab_reg = -2 * grab_reg + lambda * coeff_reg / hls::abs(coeff_reg);
		}

        if (i < basic_depth / 2 || i > coeff_depth - basic_depth / 2) {
			grab_compare = fixed(hls::abs(grab_reg) > hls::abs(grab_compare) ? hls::abs(grab_reg) : hls::abs(grab_compare));
		}
        
        grab_memory[is] = grab_reg;
    }
    if (grab_compare < complete_threshold) {
        *opt_complete = 1;
    }
}

// float CostFunctionOpt(float* basic_memory,
// 					float* coeff_memory,
// 					float* patch_memory,
// 					float* delta_memory,
// 					float* grab_memory,
// 					int* opt_complete,
// 					int grab_rank,
// 					int coeff_rank
// ) {
//     float cost = 0;

// #pragma HLS DATAFLOW
//     cost = compute_conv_and_cost(basic_memory, coeff_memory, patch_memory, delta_memory, coeff_rank);
//     compute_gradient(basic_memory, delta_memory, grab_memory, grab_rank);
//     finalize_gradients_and_check_optimization(coeff_memory, grab_memory, coeff_rank, opt_complete);
    
//     return cost;
// }

extern "C" {
    void cost_func(
        float basic_memory[basic_depth],
        float coeff_memory[(coeff_depth + 1) * 2],
        float patch_memory[patch_depth],
        float delta_memory[basic_depth],
        float grab_memory[(coeff_depth + 1) * 2],
        int* opt_complete,
        int grab_rank, 
        int coeff_rank_out, 

        float* cost
    ) {
#pragma HLS INTERFACE m_axi port=basic_memory offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=coeff_memory offset=slave bundle=gmem1
#pragma HLS INTERFACE m_axi port=patch_memory offset=slave bundle=gmem2
#pragma HLS INTERFACE m_axi port=delta_memory offset=slave bundle=gmem3
#pragma HLS INTERFACE m_axi port=grab_memory offset=slave bundle=gmem4 
#pragma HLS INTERFACE m_axi port=opt_complete offset=slave bundle=gmem5
#pragma HLS INTERFACE s_axilite port=grab_rank bundle=control
#pragma HLS INTERFACE s_axilite port=coeff_rank_out bundle=control
#pragma HLS INTERFACE m_axi port=cost offset=slave bundle=gmem6

#pragma HLS INTERFACE s_axilite port=return  bundle=control

        fixed local_basic_memory[basic_depth];
#pragma HLS ARRAY_PARTITION variable=local_basic_memory block factor=16
        fixed local_coeff_memory[(coeff_depth + 1) * 2];
#pragma HLS ARRAY_PARTITION variable=local_coeff_memory block factor=16
        fixed local_patch_memory[patch_depth];
#pragma HLS ARRAY_PARTITION variable=local_patch_memory block factor=16

        fixed local_delta_memory[basic_depth];
#pragma HLS ARRAY_PARTITION variable=local_delta_memory block factor=16
        fixed local_grab_memory[(coeff_depth + 1) * 2];
#pragma HLS ARRAY_PARTITION variable=local_grab_memory block factor=16

        read_in:
        for (int i = 0; i < basic_depth; ++i) {
    #pragma HLS pipeline
            local_basic_memory[i] = (fixed) basic_memory[i];
            local_patch_memory[i] = (fixed) patch_memory[i];
            local_delta_memory[i] = (fixed) delta_memory[i];
        }
        for (int i = 0; i < (coeff_depth + 1) * 2; i++) {
    #pragma HLS pipeline
            local_coeff_memory[i] = (fixed) coeff_memory[i];
            local_grab_memory[i] = (fixed) grab_memory[i];
        }


		compute_conv_and_cost(local_basic_memory, local_coeff_memory, local_patch_memory, local_delta_memory, coeff_rank_out, cost);
		compute_gradient(local_basic_memory, local_delta_memory, local_grab_memory, grab_rank);
		finalize_gradients_and_check_optimization(local_coeff_memory, local_grab_memory, coeff_rank_out, opt_complete);

		// std::cout << "TOP LEVEL FUNCTION: cost = " << std::endl;	
        write_back:
        for (int i = 0; i < basic_depth; ++i) {
    #pragma HLS pipeline
            delta_memory[i] = (float) local_delta_memory[i];
        }
        for (int i = 0; i < (coeff_depth + 1) * 2; i++) {
    #pragma HLS pipeline
            grab_memory[i] = (float) local_grab_memory[i];
        }

    }
}

"""