from PIL import Image
import numpy
import os
import bisect

# value of terms
z1 = complex(0, 0) # complex(0)
center = complex(1, 0)

# attributes for sequence generation
sequence_repeats = 100
ceiling = 1000000000
rounding = 10

# attributes for diagram generation
pixel_precision = 800
num_gridlines = 0
image_name = "image.png"

# attributes for gif generation
num_images = 60
starting_size = 5 # 5
ending_size = 0.00001


def format_complex_number(num):
    formatted_real = str(round(num.real, rounding))
    rounded_imag = round(num.imag, rounding)
    formatted_imag = str(rounded_imag)
    if rounded_imag >= 0:
        return formatted_real + "+" + formatted_imag + "i"
    return formatted_real + formatted_imag + "i"


def generate_next_term(previous_term, c):
    return previous_term ** 2 + c


def test_divergence(z, c):
    # formatted_c = format_complex_number(c)

    # print("z1 = " + format_complex_number(z))

    for i in range(sequence_repeats):
        next_term = generate_next_term(z, c)

        # text = [
        #     "z" + str(i + 2),
        #     "(z" + str(i + 1) + ")^2 + " + formatted_c,
        #     "(" + str(format_complex_number(z)) + ")^2 + " + formatted_c,
        #     str(format_complex_number(z ** 2)) + " + " + formatted_c,
        #     str(format_complex_number(next_term)),
        #     str(round(abs(next_term), 10))
        # ]
        # print(" = ".join(text))

        z = next_term
        modulus = abs(z)
        if modulus > ceiling:
            return i
    return sequence_repeats


colors = [(0, 0, 0), (20, 11, 52), (132, 32, 107), (229, 92, 48), (246, 215, 70), (255, 255, 255)]
len_colors = len(colors) - 1


def value_to_single_color(c, floored_c, color):
    try:
        return round((colors[floored_c + 1][color] - colors[floored_c][color]) * (c - floored_c) + colors[floored_c][color])
    except:
        print(floored_c)
        print(color)
        print(c)
        return 255

def value_to_rgb_color(value):
    if value == 1.0:
        return 255, 255, 255
    c = value * len_colors
    floored_c = int(c)
    return value_to_single_color(c, floored_c, 0), value_to_single_color(c, floored_c, 1), value_to_single_color(c, floored_c, 2)


def test_divergence_across_range_c(z, c, size):
    starting_num = c - complex(size / 2, size / 2)
    step = size / pixel_precision
    values = []
    value_range = []
    for i in range(pixel_precision):
        values.append([])
        for j in range(pixel_precision):
            value = test_divergence(z, starting_num + complex(i, j) * step)
            if value not in value_range:
                value_range.append(value)
            values[-1].append(value)

    return values, sorted(value_range)

def test_divergence_across_range_z(z, c, size):
    starting_num = z - complex(size / 2, size / 2)
    step = size / pixel_precision
    values = []
    value_range = []
    for i in range(pixel_precision):
        values.append([])
        for j in range(pixel_precision):
            value = test_divergence(starting_num + complex(i, j) * step, c)
            if value not in value_range:
                value_range.append(value)
            values[-1].append(value)

    return values, sorted(value_range)

def round_to_closest(num, base):
    return round(num / base) * base

def display_divergence_across_range(values, value_range):
    max_value = value_range[-1]
    img = Image.new('RGB', (pixel_precision, pixel_precision), "black")
    pixels = img.load()
    # half = round(pixel_precision / 2)
    # gridline = round(pixel_precision / (num_gridlines + 2))
    for i in range(pixel_precision):
        for j in range(pixel_precision):
            # if i == half or j == half:
            #     pixels[i, pixel_precision - j - 1] = (255, 0, 0)
            #     continue
            # if i != 0 and j != 0 and (i % gridline == 0 or j % gridline == 0):
            #     pixels[i, pixel_precision - j - 1] = (0, 255, 0)
            #     continue
            color = values[i][j] / max_value
            pixels[i, pixel_precision - j - 1] = value_to_rgb_color(color)
    return img


def display_divergence_on_point(z, c, starting_size, ending_size, num_images, switch):
    images = []
    for i, size in enumerate(numpy.geomspace(starting_size, ending_size, num_images)):
        print("Loading image " + str(i + 1) + " out of " + str(num_images))
        if switch:
            values, value_range = test_divergence_across_range_c(z, c, size)
        else:
            values, value_range = test_divergence_across_range_z(c, z, size)
        img = display_divergence_across_range(values, value_range)
        images.append(img)

    save_images(images)

def display_divergence_around_point(starting_z, starting_c, size, num_images, switch):
    images = []
    full_circle = numpy.pi * 2
    for i in range(num_images):
        print("Loading image " + str(i + 1) + " out of " + str(num_images))
        argument = full_circle * i / num_images
        if switch:
            z = starting_z * complex(numpy.cos(argument), numpy.sin(argument))
            values, value_range = test_divergence_across_range_c(z, starting_c, size)
        else:
            c = starting_c * complex(numpy.cos(argument), numpy.sin(argument))
            values, value_range = test_divergence_across_range_z(starting_z, c, size)
        img = display_divergence_across_range(values, value_range)
        images.append(img)

    save_images(images)

def save_images(images):
    i = 0
    while os.path.isfile(f"mandelbrot{i}.gif"):
        i += 1

    images[0].save(f"mandelbrot{i}.gif", save_all=True, append_images=images[1:], loop=0)

# def display_divergence_on_point(z, point, starting_size, ending_size, num_images):
#     images = []
#     for i, size in enumerate(numpy.geomspace(starting_size, ending_size, num_images)):
#         print("Loading image " + str(i + 1) + " out of " + str(num_images))
#         img = display_divergence_across_range(z, point, size)
#         images.append(img)
#
#     images[0].save("mandelbrot2.gif", save_all=True, append_images=images[1:])


# display_divergence_on_point(z1, center, starting_size, ending_size, num_images, False)
display_divergence_around_point(z1, center, starting_size, num_images, False)
# display_divergence_around_point(center, z1, starting_size, num_images, True)