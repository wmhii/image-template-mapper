from PIL import Image
import numpy as np
from itertools import product
import typing
import argparse


def pack_rgb(rgb: typing.Union[tuple, np.ndarray]) -> int:
    rgb_int = (rgb[0] << 16)
    rgb_int |= (rgb[1] << 8)
    rgb_int |= rgb[2]
    return rgb_int


def unpack_rgb(rgb_int: int) -> tuple:
    red = (rgb_int >> 16) & 0xFF
    green = (rgb_int >> 8) & 0xFF
    blue = rgb_int & 0xFF
    return red, green, blue


def pack_rgb_image(im: Image.Image) -> np.array:
    pixels = np.asarray(im)
    size = (im.size[1], im.size[0])
    mapped_pixels = np.empty(size, dtype=np.int32)

    x_size = im.size[0]
    y_size = im.size[1]
    for x, y in product(range(x_size), range(y_size)):
        mapped_pixels[y, x] = pack_rgb(pixels[y, x])

    return mapped_pixels


def average_color(color1, color2):
    return unpack_rgb(int((pack_rgb(color1) + pack_rgb(color2))/2))


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
    parser = argparse.ArgumentParser(prog="ImageToMap2",
                                     description='Maps the colors of one image to the form of another')

    parser.add_argument("colors_image",
                        help="The image that provides initial color pallet")

    parser.add_argument("template",
                        help="An image that provides the positions of the colors")

    parser.add_argument('-o', '--output',
                        default="out_image.png",
                        help="File location for the resulting map (default: out_image.png")
    args = parser.parse_args()

    image = Image.open(args.colors_image)
    template = Image.open(args.template)
    out_image = map_image(image, template)
    out_image.save(args.output)

