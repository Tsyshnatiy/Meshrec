import os
import glob
import numpy as np

def take_cat_npys(root_path, category):
    npy_wildcard = root_path + os.sep + '**' + os.sep + '{}*.npy'.format(category)
    return glob.glob(npy_wildcard, recursive=True)

def get_categories(dataset_root):
    test_dir = dataset_root + os.sep + 'test'
    return [d for d in os.listdir(test_dir) if os.path.isdir(test_dir + os.sep + d)]

def png_path_from_npy_path(npy_path):
    idx = npy_path.rfind('.')
    return npy_path[:idx] + '.png'

def mse(img1, img2):
    el_number = img1.shape[0] * img1.shape[1]
    return np.sum((img1 - img2) ** 2) / el_number
