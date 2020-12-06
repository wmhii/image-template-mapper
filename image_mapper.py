import ctypes
import timeit
from ctypes import cdll

import numpy as np
from PIL import Image
from numpy.ctypeslib import ndpointer

# To see the profiling reults of the CUDA code, call this script with: nvprof python image_mapper.py
num_runs = 1

# link to .dll and set up expected function arguments
my_dll = cdll.LoadLibrary(r"C:\ProgramData\NVIDIA Corporation\CUDA Samples\v11.0\x64\Release\FinalProject.dll")

do_parallel = my_dll.parallelImageTemplateMap
do_parallel.restype = ctypes.c_int
do_parallel.argtypes = [ndpointer(ctypes.c_uint8, flags='C_CONTIGUOUS'),
                        ndpointer(ctypes.c_uint8, flags='C_CONTIGUOUS'),
                        ndpointer(ctypes.c_uint8, flags='C_CONTIGUOUS'),
                        ndpointer(ctypes.c_uint8, flags='C_CONTIGUOUS'),
                        ctypes.c_uint,
                        ctypes.c_uint]

do_serial = my_dll.serialImageTemplateMap
do_serial.restype = ctypes.c_int
do_serial.argtypes = [ndpointer(ctypes.c_uint8, flags='C_CONTIGUOUS'),
                      ndpointer(ctypes.c_uint8, flags='C_CONTIGUOUS'),
                      ndpointer(ctypes.c_uint8, flags='C_CONTIGUOUS'),
                      ndpointer(ctypes.c_uint8, flags='C_CONTIGUOUS'),
                      ctypes.c_uint,
                      ctypes.c_uint]


# Load the images and force RGBA format.
template = Image.open('circles.png').convert('RGBA')
colors = Image.open('mountain.png').convert('RGBA')

# resize template so CUDA doesn't fail, make sure the colors image is the same size
template = template.resize((500, 300))
colors = colors.resize(template.size)

# Create numpy arrays to pass to the functions
template_arr = np.array(template, dtype=np.uint8)
colors_arr = np.array(colors, dtype=np.uint8)
out_arr = np.zeros(colors_arr.shape, dtype=np.uint8)

template_arr[:, :, 3] = 255  # set alpha to 255 for all pixels

# create the array of unique colors from the template image
list_of_colors = np.array([c for count, c, in template.getcolors(template_arr.size)], dtype=np.uint8)

print(f'Number of pixles: {template_arr.size//4}')
print(f'Number of unique colors: {list_of_colors.size//4}')


# Run the CUDA code
print(f'calling CUDA function {num_runs} times')
for i in range(num_runs):
    result = do_parallel(out_arr, colors_arr, template_arr, list_of_colors, out_arr.size // 4, list_of_colors.size // 4)
    if result != 0:
        print(f'Cuda Error: {result}')
        exit(result)
print('finished CUDA')

# Run the serial code
print(f'calling Serial function {num_runs} times')
cpu_time = timeit.timeit(lambda: do_serial(out_arr, colors_arr, template_arr, list_of_colors, out_arr.size//4, list_of_colors.size//4), number=num_runs)
print(f'average cpu in {num_runs} runs time: {cpu_time/num_runs}s')

out = Image.fromarray(out_arr)
out.show()
