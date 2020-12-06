
#include "cuda_runtime.h"
#include "device_launch_parameters.h"

#include <stdio.h>
#include <stdint.h>

#define ALPHA 0xFF000000
#define THREADS 512 
#define BLOCKS 256 

__global__ void imageMapKernel(uint8_t*out_image,
						  const uint8_t *colors_image,
						  const uint32_t *template_image,
						  const uint32_t *colors_list, 
						  unsigned int image_size,
						  unsigned int colors_size)
{
	uint32_t color = 0;
	float average_r;
	float average_g;
	float average_b;
	uint32_t compare_color = 0;
	
	for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < colors_size; i += blockDim.x * gridDim.x) {
		unsigned int x = 0;
		compare_color = colors_list[i];

		// Search for the first color
		for (x = 0; x < image_size; x++) {
			if (template_image[x] == compare_color) {
				average_r = (float)colors_image[x*4+0]; // future improvement, read from memory once and do the binary arithmetic
				average_g = (float)colors_image[x*4+1];
				average_b = (float)colors_image[x*4+2];
				break;
			}
		}
		// Average in the rest of the colors
		for (; x < image_size; x++) {
			if (template_image[x] == compare_color) {
				average_r = (average_r + (float)colors_image[x*4+0])/2.0f;
				average_g = (average_g + (float)colors_image[x*4+1])/2.0f;
				average_b = (average_b + (float)colors_image[x*4+2])/2.0f;
			}
		}

		// Write out the final averaged color
		for (x = 0; x < image_size; x++) {
			if (template_image[x] == compare_color) {
				out_image[x*4+0] = (uint8_t)average_r;
				out_image[x*4+1] = (uint8_t)average_g;
				out_image[x*4+2] = (uint8_t)average_b;
				out_image[x*4+3] = 255;
			}
		}
	}
}

extern "C" {
	__declspec(dllexport)

	cudaError_t parallelImageTemplateMap(uint8_t* out_image,
		                                 uint8_t* colors_image,
		                                 uint8_t* template_image,
		                                 uint8_t* colors_list,
		                                 unsigned int image_size, 
		                                 unsigned int colors_size)
	{
		uint8_t *dev_out = 0;
		uint8_t *dev_colors = 0;
		uint32_t *dev_template = 0;
		uint32_t *dev_list = 0;

		unsigned int image_bytes = image_size * 4;
		unsigned int colors_bytes = colors_size * 4;

		cudaError_t cudaStatus;

		cudaStatus = cudaSetDevice(0);
		if (cudaStatus != cudaSuccess) {
			printf("cudaSetDevice failed!");
			goto Error;
		}

		// Allocate GPU buffers for three images (two input, one output) and the unique colors array.
		cudaStatus = cudaMalloc((void**)&dev_out, image_bytes);
		if (cudaStatus != cudaSuccess) {
			printf("devOut cudaMalloc failed!");
			goto Error;
		}

		cudaStatus = cudaMalloc((void**)&dev_colors, image_bytes);
		if (cudaStatus != cudaSuccess) {
			printf("devColors cudaMalloc failed!");
			goto Error;
		}

		cudaStatus = cudaMalloc((void**)&dev_template, image_bytes);
		if (cudaStatus != cudaSuccess) {
			printf("devTemplate cudaMalloc failed!");
			goto Error;
		}

		cudaStatus = cudaMalloc((void**)&dev_list, colors_bytes);
		if (cudaStatus != cudaSuccess) {
			printf("devList cudaMalloc failed!");
			goto Error;
		}

		// Copy input vectors from host memory to GPU buffers.
		cudaStatus = cudaMemcpy((void*)dev_colors, (void*)colors_image, image_bytes, cudaMemcpyHostToDevice);
		if (cudaStatus != cudaSuccess) {
			printf("devColors cudaMemcpy failed!");
			goto Error;
		}

		cudaStatus = cudaMemcpy((void*)dev_template, (void*)template_image, image_bytes, cudaMemcpyHostToDevice);
		if (cudaStatus != cudaSuccess) {
			printf("devTemplate cudaMemcpy failed!");
			goto Error;
		}

		cudaStatus = cudaMemcpy((void*)dev_list, (void*)colors_list, colors_bytes, cudaMemcpyHostToDevice);
		if (cudaStatus != cudaSuccess) {
			printf("devList cudaMemcpy failed!");
			goto Error;
		}

		cudaStatus = cudaMemset((void*)dev_out, 0, image_bytes);
		if (cudaStatus != cudaSuccess) {
			printf("dev_out memset failed!");
			goto Error;
		}

		// Launch a kernel on the GPU with one thread for each element.
		imageMapKernel <<<BLOCKS, THREADS>>> (
			dev_out,
			dev_colors,
			dev_template,
			dev_list,
			image_size,
			colors_size);

		// Check for any errors launching the kernel
		cudaStatus = cudaGetLastError();
		if (cudaStatus != cudaSuccess) {
			printf("imageMapKernel launch failed: %s\n", cudaGetErrorString(cudaStatus));
			goto Error;
		}

		// cudaDeviceSynchronize waits for the kernel to finish, and returns
		// any errors encountered during the launch.
		cudaStatus = cudaDeviceSynchronize();
		if (cudaStatus != cudaSuccess) {
			printf("cudaDeviceSynchronize returned error code %d after launching imageMapKernel!\n", cudaStatus);
			goto Error;
		}

		// Copy output vector from GPU buffer to host memory.
		cudaStatus = cudaMemcpy(out_image, dev_out, image_bytes, cudaMemcpyDeviceToHost);
		if (cudaStatus != cudaSuccess) {
			printf("outImage cudaMemcpy failed!");
			goto Error;
		}

	Error:
		cudaFree(dev_out);
		cudaFree(dev_colors);
		cudaFree(dev_template);
		cudaFree(dev_list);

		return cudaStatus;
	}


	__declspec(dllexport)
	int serialImageTemplateMap(uint8_t* out_image,
		uint8_t* colors_image,
		uint8_t* template_image,
		uint8_t* colors_list,
		unsigned int image_size,
		unsigned int colors_size) {
		
		uint32_t* temp = (uint32_t*)template_image;
		uint32_t* list = (uint32_t*)colors_list;

		uint32_t compare_color = 0;
		float average_r = 0;
		float average_g = 0;
		float average_b = 0;

		unsigned int color_index = 0;
		for (int i = 0; i < colors_size; i++) {
			compare_color = list[i];
			int x = 0;
			// Search for the first color
			for (x = 0; x < image_size; x++) {
				if (temp[x] == compare_color) {
					average_r = (float)colors_image[x * 4 + 0]; // Future improvment: read from the array once and do the binary arithmetic.
					average_g = (float)colors_image[x * 4 + 1];
					average_b = (float)colors_image[x * 4 + 2];
					break;
				}
			}

			// Average in the rest of the colors
			for (; x < image_size; x++) {
				if (temp[x] == compare_color) {
					average_r = (average_r + (float)colors_image[x * 4 + 0])/2.0f;
					average_g = (average_g + (float)colors_image[x * 4 + 1])/2.0f;
					average_b = (average_b + (float)colors_image[x * 4 + 2])/2.0f;
				}
			}

			// Write out the final average color
			for (x = 0; x < image_size; x++) {
				if (temp[x] == compare_color) {
					out_image[x * 4 + 0] = (uint8_t)average_r;
					out_image[x * 4 + 1] = (uint8_t)average_g;
					out_image[x * 4 + 2] = (uint8_t)average_b;
					out_image[x * 4 + 3] = 255;
				}
			}
		}
		return 0;
	}

}
