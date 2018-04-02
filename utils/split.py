import os
import glob
from random import shuffle

import utils
from utils import *

# what is the path where element currectly is
# where is 'train', 'test' or 'validation'
def save_to(what, root_path, where, cat):
    target_dir = root_path + os.sep + where + os.sep + cat
    target = target_dir + os.sep + os.path.basename(what)
    if target == what:
        return
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    os.rename(what, target)
    os.rename(utils.png_path_from_npy_path(what), utils.png_path_from_npy_path(target))
    
def split(root_path, train_prop, test_prop):
    val_prop = 1 - train_prop - test_prop
    
    categories = utils.get_categories(root_path)
    
    for cat in categories:
        npy_path_list = utils.take_cat_npys(root_path, cat)
        n = len(npy_path_list)
        
        train_number = int(n * train_prop)
        test_number = int(n * test_prop)
        val_number = int(n * val_prop)
        
        shuffle(npy_path_list)
        
        for i in range(train_number):
            save_to(npy_path_list[i], root_path, 'train', cat)
        for i in range(train_number, train_number + test_number):
            save_to(npy_path_list[i], root_path, 'test', cat)
        for i in range(train_number + test_number, n):
            save_to(npy_path_list[i], root_path, 'validation', cat)


if __name__ == "__main__":
    import sys
    root_path = sys.argv[1]
    train_prop = float(sys.argv[2])
    test_prop = float(sys.argv[3])
    split(root_path, train_prop, test_prop)
