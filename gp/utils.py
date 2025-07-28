import json
import os


def create_directory(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)


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
