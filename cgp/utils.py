import csv
import datetime
import json
import os
import imageio
import numpy as np
from matplotlib import pyplot as plt


def load_img(img_path):
    """
    It takes in a path to an image, loads the image, and returns the image

    :param img_path: The path to the image you want to load
    :return: The image is being returned.
    """
    img = plt.imread(img_path)
    return img


def show_img(img):
    """
    It takes an image and displays it

    :param img: the image to be processed
    """
    img = img.astype(np.uint8)
    plt.imshow(img)
    plt.show()


def save_img(path, individual, image):
    filename = path + "/" + str(individual) + ".png"
    image = image.astype(np.uint8)
    imageio.imwrite(filename, image)


def export_images(population, destination):
    index = 0
    for individual in population:
        save_img(destination, index, individual.data)
        index += 1


def create_white_img(width, height):
    """
    > This function creates a white image of the specified width and height

    :param width: The width of the image in pixels
    :param height: The height of the image in pixels
    :return: A white image of the specified width and height.
    """
    img = np.zeros([width, height, 3], dtype=np.uint8)
    return img


def create_random_img(width, height):
    img = np.random.rand(width, height, 3) * 255
    img = img.astype(np.uint8)
    return img


def get_current_timestamp():
    """
    It takes the current time, converts it to a string, removes the decimal point and the digits after it, replaces the
    dashes, colons, and spaces with underscores, and returns the result.
    :return: A string of the current time in the format of year_month_day_hour_minute_second
    """
    ct = datetime.datetime.now()

    timestamp = str(ct)
    timestamp = timestamp[:timestamp.find('.')]
    timestamp = timestamp.replace('-', '_').replace(':', '_').replace(' ', '_')

    return timestamp


def create_directory(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)


def write_to_file(filename, data):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def list_to_str(list_array):
    """
    It takes a list of numbers and returns a string of the form "[1;2;3;4;5]"

    :param list_array: the list of numbers you want to convert to a string
    :return: A string of the list_array with each element separated by a semicolon.
    """
    return "[" + ';'.join(map(str, list_array)) + "]"


def load_configs(filename):
    """
    It opens the file, reads the JSON, and returns the result

    :param filename: the name of the file to load the configuration from
    :return: A dictionary with the contents of the json file.
    """
    result = {}
    with open(filename, 'r') as f:
        result.update(json.load(f))
    return result
