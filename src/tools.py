from src.config import directories
import shutil
import os


def remove_dirs():
    for folder in directories:
        if os.path.exists(folder):
            shutil.rmtree(folder)#


def create_dirs():
    for folder in directories:
        if not os.path.exists(folder):
            os.mkdir(folder)
