import argparse
from enum import Enum
from itertools import product
import numpy as np
from PIL import Image, ImageCms

# image transformations from RGB->LAB and LAB->RGB
rgb_p = ImageCms.createProfile('sRGB')
lab_p = ImageCms.createProfile('LAB')


rgb2lab = ImageCms.buildTransformFromOpenProfiles(rgb_p, lab_p, "RGB", "LAB")
lab2rgb = ImageCms.buildTransformFromOpenProfiles(lab_p, rgb_p, "LAB", "RGB")


class Mode(Enum):
    RGB = 'RGB'
    LAB = 'LAB'
    HSV = 'HSV'

    def __str__(self):
        return self.value


def pack_rgb_image(im: Image.Image) -> np.array:
    """Takes a standard three dimensional array (x, y, rgb) and converts it to a two dimensional array (x, y)
        where the values stored are single 32-bit rgb integers
    """
    arr = np.array(im)
    x_size, y_size, _ = arr.shape

    out = np.zeros((x_size, y_size, 4), dtype=np.uint8)
    out[:, :, 0:3] = arr  # copy the original array into the out array (will produce [r, g, b, 0] arrays)
    out = out.view(dtype=np.uint32)  # View the [r, g, b, 0] array as a 32-big integer
    out = out.reshape(arr.shape[:-1])  # Remove the third dimension
    return out


def map_image(image: Image.Image, template: Image.Image, mode: Mode) -> Image.Image:
    """Create a color/template mapped image with the given images

    The form of the final image will come from the template
    The colors of the final image will come from the image
    """
    # Resize the image to be the same as the template
    size = template.size
    image = image.resize(size)

    # Pick the right dtype, as the a and b in LAB has a range of [-100, 100]
    if mode == Mode.LAB:
        dtype = np.int8
    else:
        dtype = np.uint8

    # Grab pixel arrays of each image (with respective conversions)
    # and convert the colors image to L*a*b color space
    image_pix = np.array(image, dtype=dtype)
    template_pix = pack_rgb_image(template)

    # Here is where we build the color mapping
    colors = dict()
    for y, x in product(range(size[0]), range(size[1])):
        t_pix = template_pix[x, y]
        i_pix = image_pix[x, y]

        if t_pix not in colors:
            colors[t_pix] = []

        colors[t_pix].append(i_pix)

    # Mix the collected colors (A simple average)
    for key, value in colors.items():
        colors[key] = np.mean(value, axis=0, dtype=np.float64)

    # Create an image to apply the final mapping
    mapped_pixels = np.zeros((size[1], size[0], 3), dtype=dtype)

    # Apply the color map
    for y, x in product(range(size[0]), range(size[1])):
        t_pix = colors[template_pix[x, y]].astype(dtype)
        mapped_pixels[x, y] = t_pix

    mapped_image = Image.fromarray(mapped_pixels, mode.value)

    return mapped_image


def main():
    parser = argparse.ArgumentParser(prog='ImageToMap',
                                     description='Maps the colors of one image to the form of another')

    parser.add_argument('colors_image',
                        help='The image that provides initial color pallet')

    parser.add_argument('template_image',
                        help='An image that provides the positions of the colors')

    parser.add_argument('-o', '--output',
                        default='out_image.png',
                        help='File location for the resulting map (default: out_image.png')

    parser.add_argument('--mode',
                        type=Mode,
                        choices=list(Mode),
                        default=Mode.RGB,
                        help='Color model to use for mixing the images together.',)

    args = parser.parse_args()

    image = Image.open(args.colors_image)
    template = Image.open(args.template_image)

    # Make sure the image starts out in RGB mode.
    image = image.convert('RGB')
    template = template.convert('RGB')

    # Convert the image to the specified mode
    if args.mode == Mode.LAB:
        image = ImageCms.applyTransform(image, rgb2lab)
    elif args.mode == Mode.HSV:
        image = image.convert('HSV')

    out_image = map_image(image, template, args.mode)

    # Convert the image back to RGB space so we can save it.
    if args.mode == Mode.LAB:
        out_image = ImageCms.applyTransform(out_image, lab2rgb)
    else:
        out_image = out_image.convert('RGB')

    out_image.save(args.output)


if __name__ == '__main__':
    main()
