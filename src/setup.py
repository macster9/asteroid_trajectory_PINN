from src.tools import *
from src.config import directories
import os
import shutil


def remove_dirs():
    """
    Clears all directories.
    :return: None
    """
    for folder in gen_dict_extract("data", directories["data"]):
        if os.path.exists(folder):
            shutil.rmtree(folder)
    return print("Removed all directories.")


def create_dirs():
    """
    Creates all directories
    :return: None
    """
    for folder in gen_dict_extract("data", directories["data"]):
        if not os.path.exists(folder):
            os.mkdir(folder)
    return print("Directory structure created.")


def del_temp_files():
    """
    Deletes all temporary files.
    :return: Remove tree of data/temp
    """
    shutil.rmtree("data/temp")
    return print("Temp files deleted.")
