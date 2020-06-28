from uuid import uuid4

from PIL import Image, ImageColor
import numpy as np

BASE_OUTSIDE_RED = 0
BASE_OUTSIDE_GREEN = 0
BASE_OUTSIDE_BLUE = 0
BASE_INSIDE_RED = 255
BASE_INSIDE_GREEN = 255
BASE_INSIDE_BLUE = 255


def create_heart(inside_hex, outside_hex):
    outside_rgb = ImageColor.getcolor(outside_hex, "RGB")
    inside_rgb = ImageColor.getcolor(inside_hex, "RGB")
    print(outside_rgb, inside_rgb)

    base_heart_image = Image.open("images/base.png")
    base_heart_image = base_heart_image.convert('RGBA')

    image_data = np.array(base_heart_image)
    red, green, blue, alpha = image_data.T

    inside_areas = (red == BASE_INSIDE_RED) & (green == BASE_INSIDE_GREEN) & (blue == BASE_INSIDE_BLUE)
    image_data[..., :-1][inside_areas.T] = inside_rgb

    outside_areas = (red == BASE_OUTSIDE_RED) & (green == BASE_OUTSIDE_GREEN) & (blue == BASE_OUTSIDE_BLUE)
    image_data[..., :-1][outside_areas.T] = outside_rgb

    converted_heart = Image.fromarray(image_data)
    converted_heart.save('out/heart-' + str(uuid4()) + ".png")
    converted_heart.show()


create_heart("#FF0000", "#800000")
