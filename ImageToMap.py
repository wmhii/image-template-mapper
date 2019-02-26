from PIL import Image
import numpy as np
import math
from itertools import product
import argparse

# reference = [109.850, 100.000, 35.585]
# reference = [95.044, 100.000, 108.755]
reference = [94.811, 100.000, 107.304]

def pack_rgb_image(im: Image.Image) -> np.array:
    arr = np.array(im)
    x_size, y_size, _ = arr.shape
    out = np.zeros((x_size, y_size, 4), dtype=np.uint8)
    out[:,:,0:3] = arr
    out = out.view(dtype=np.uint32)
    out = out.reshape(arr.shape[:-1])
    return out

def convert_image_to_lab(arr:np.array):
    converted = arr.astype(dtype=np.float64)
    for x, y in product(range(arr.shape[0]),range( arr.shape[1])):
        converted[x,y] = convert_rgb_to_lab(arr[x,y])
    return converted

def convert_rgb_to_lab(color:np.array):

    # first we have to convert to XYZ space
    xyz = color/255.0

    for i in range(3):
        if xyz[i] > 0.04045:
            xyz[i] = math.pow((xyz[i] + 0.055)/1.055, 2.4)
        else:
            xyz[i] = xyz[i]/12.92

    xyz = xyz*100

    lab = xyz.copy()

    lab[0] = xyz[0] * 0.4124 + xyz[1] * 0.3576 + xyz[2] * 0.1805
    lab[1] = xyz[0] * 0.2126 + xyz[1] * 0.7152 + xyz[2] * 0.0722
    lab[2] = xyz[0] * 0.0193 + xyz[1] * 0.1192 + xyz[2] * 0.9505

    # now to convert to LAB

    lab[0] /= reference[0]
    lab[1] /= reference[1]
    lab[2] /= reference[2]

    for i in range(3):
        if lab[i] > 0.008856:
            lab[i] = math.pow(lab[i], 1.0/3.0)
        else:
            lab[i] = (7.787 * lab[i]) + (16.0 / 116.0)

    final = lab.copy()

    final[0] = (116 * lab[1]) - 16
    final[1] = 500 * (lab[0] - lab[1])
    final[2] = 200 * (lab[1] - lab[2])

    return final


def convert_lab_to_rgb(color:np.array):
    # first we have to convert to XYZ

    xyz = color.copy()/1.0
    xyz[1] = (color[0] + 16.0) / 116.0
    xyz[0] = color[1]/500.0 + xyz[1]
    xyz[2] = xyz[1] - color[2]/200.0

    for i in range(3):
        if math.pow(xyz[i], 3) > 0.008856:
            xyz[i] = math.pow(xyz[i], 3)
        else:
            xyz[i] = (xyz[i] - 16 / 116.0) / 7.787


    xyz[0] = xyz[0] * reference[0]
    xyz[1] = xyz[1] * reference[1]
    xyz[2] = xyz[2] * reference[2]

    xyz = xyz/100.0

    rgb = xyz.copy()

    rgb[0] = xyz[0] * 3.2406 + xyz[1] * -1.5372 + xyz[2] * -0.4986
    rgb[1] = xyz[0] * -0.9689 + xyz[1] * 1.8758 + xyz[2] * 0.0415
    rgb[2] = xyz[0] * 0.0557 + xyz[1] * -0.2040 + xyz[2] * 1.0570

    for i in range(3):
        if rgb[i] > 0.0031308:
            rgb[i] = 1.055 * math.pow(rgb[i], 1/2.4) - 0.055
        else:
            rgb[i] = 12.92 * rgb[i]
    rgb *= 255

    return rgb.astype(np.uint8)


def map_image(image: Image.Image, template: Image.Image) -> Image.Image:
    size = template.size
    image = image.resize(size)

    if not image.mode == 'RGB':
        image = image.convert('RGB')

    if not template.mode == 'RGB':
        template = template.convert('RGB')


    image_pix = convert_image_to_lab(np.array(image))
    template_pix = pack_rgb_image(template)

    colors = dict()
    for y, x in product(range(size[0]), range(size[1])):
        t_pix = template_pix[x, y]
        i_pix = image_pix[x, y]

        if t_pix not in colors:
            colors[t_pix] = []

        colors_list = colors[t_pix]
        colors_list.append(i_pix)

    for key, value in colors.items():
        colors[key] = convert_lab_to_rgb(np.mean(value, axis=0, dtype=np.float64))

    mapped_image: Image.Image = Image.new('RGB', size)
    mapped_pixels = mapped_image.load()

    for y, x in product(range(size[0]), range(size[1])):
        t_pix = tuple(colors[template_pix[x, y]])
        mapped_pixels[y, x] = t_pix


    return mapped_image


def test_conversions():
    from itertools import product
    for r, g in product(range(255), range(255)):
        b = 120
        orig = np.array((r, g, b), dtype=np.uint8)
        lab = convert_rgb_to_lab(orig)
        back = convert_lab_to_rgb(lab)
        print(f'[{orig[0]}, {orig[1]}, {orig[2]}] -> [{lab[0]}, {lab[1]}, {lab[2]}] -> [{back[0]}, {back[1]}, {back[2]}]')

# if __name__ == '__main__':
#     import cProfile
#     import pstats
#     # image = Image.open('caleb.png')
#     # template = Image.open('abstract.png')
#     # map_image(image, template)
#     # cProfile.run('map_image(image, template)', 'stats')
#
#     p = pstats.Stats('stats')
#     p.strip_dirs().sort_stats('tottime').print_stats()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="ImageToMap",
                                     description='Maps the colors of one image to the form of another')

    parser.add_argument("colors_image",
                        help="The image that provides initial color pallet")

    parser.add_argument("template_image",
                        help="An image that provides the positions of the colors")

    parser.add_argument('-o', '--output',
                        default="out_image.png",
                        help="File location for the resulting map (default: out_image.png")
    args = parser.parse_args()


    image = Image.open(args.colors_image)
    template = Image.open(args.template_image)

    out_image = map_image(image, template)
    out_image.save(args.output)
