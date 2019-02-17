from PIL import Image
import numpy as np
from itertools import product
import argparse


def pack_rgb_image(im: Image.Image) -> np.array:
    arr = np.array(im)
    x_size, y_size, _ = arr.shape
    out = np.zeros((x_size, y_size, 4), dtype=np.uint8)
    out[:,:,0:3] = arr
    out = out.view(dtype=np.uint32)
    out = out.reshape(arr.shape[:-1])
    return out


def map_image(image: Image.Image, template: Image.Image) -> Image.Image:
    size = template.size
    image = image.resize(size)

    if not image.mode == 'HSV':
        image = image.convert('HSV')

    if not template.mode == 'RGB':
        template = template.convert('RGB')

    image_pix = np.asarray(image)
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
        colors[key] = np.mean(value, axis=0, dtype=np.uint32)

    mapped_image: Image.Image = Image.new('HSV', size)
    mapped_pixels = mapped_image.load()

    for y, x in product(range(size[0]), range(size[1])):
        t_pix = tuple(colors[template_pix[x, y]])
        mapped_pixels[y, x] = t_pix

    mapped_image = mapped_image.convert('RGB')

    return mapped_image


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
