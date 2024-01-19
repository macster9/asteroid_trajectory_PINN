from src.tools import gen_dict_extract
from src.config import directories
import os
import shutil


def remove_dirs():
    for folder in gen_dict_extract("data", directories["data"]):
        if os.path.exists(folder):
            shutil.rmtree(folder)


def create_dirs():
    for folder in gen_dict_extract("data", directories["data"]):
        if not os.path.exists(folder):
            os.mkdir(folder)
