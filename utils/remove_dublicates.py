import os
import glob
import math

import numpy as np

import utils
from utils import *

def remove_in_category(path, category, tolerance):
    npy_path_list = utils.take_cat_npys(path, category)

    i = 0
    while i < len(npy_path_list):
        img1_path = npy_path_list[i]
        img1_name = os.path.basename(img1_path)
        img1 = np.load(img1_path)
        
        j = i + 1
        while j < len(npy_path_list):
            img2_path = npy_path_list[j]
            img2_name = os.path.basename(img2_path)
            img2 = np.load(img2_path)
            if mse(img1, img2) <= tolerance:
                print('{} similar to {}'.format(img1_name, img2_name))

                png_path = utils.png_path_from_npy_path(img2_path)
                print('Removing {}'.format(img2_path))
                print('Removing {}'.format(png_path))
                os.remove(img2_path)
                os.remove(png_path)

                npy_path_list.pop(j)
            j += 1
        i += 1


def enum_categories_and_remove(dir, tolerance):
    categories = utils.get_categories(dir)
    for cat in categories:
        remove_in_category(dir, cat, tolerance)

if __name__ == "__main__":
    import sys
    tolerance = 0
    enum_categories_and_remove(sys.argv[1], tolerance)