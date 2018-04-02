import os
import glob
import numpy as np
from PIL import Image

from operator import itemgetter
from heapq import nlargest

import utils
from utils import *

def find_average_image(npy_path_list, image_hei, image_wid):
    n = len(npy_path_list)

    average_image = np.zeros([image_hei, image_wid])
    for npy_file in npy_path_list:
        npy = np.load(npy_file)
        average_image += npy / n
    
    return average_image

def compute_dist_distribution(npy_path_list, average_image):
    n = len(npy_path_list)
    result = np.empty(n)

    for i in range(n):
        cur_img = np.load(npy_path_list[i])
        result[i] = utils.mse(average_image, cur_img)

    return result

def remove_outliers(dist_path_tuples, threshold):
    result = []
    for tuple in dist_path_tuples:
        if tuple[0] < threshold:
            result.insert(0, tuple[1])
    return result

def compute_most_different_images(npy_path_list, take_n):
    n = len(npy_path_list)
    if n <= take_n:
        print('Possibly not enough data')
        return npy_path_list

    D = np.zeros([n, n], dtype=float)

    for i in range(n):
        img1 = np.load(npy_path_list[i])
        for j in range(i + 1, n):
            img2 = np.load(npy_path_list[j])
            dist = mse(img1, img2)
            D[i][j] = dist
            D[j][i] = dist

    rows_sum = np.sum(D, axis = 1)
    largest = nlargest(take_n, enumerate(rows_sum), itemgetter(1))
    return [npy_path_list[i[0]] for i in largest]

if __name__ == "__main__":
    import sys

    root_path = sys.argv[1]
    N = int(sys.argv[2])

    for cat in get_categories(root_path):
        print('Processing {}'.format(cat))

        npy_path_list = utils.take_cat_npys(root_path, cat)
        print('Totally {} {}s'.format(len(npy_path_list), cat))

        avg_img = find_average_image(npy_path_list, 64, 160)
        distances = compute_dist_distribution(npy_path_list, avg_img)

        sigma = np.std(distances)
        threshold = 3 * sigma
        print('Sigma = {}'.format(sigma))
        print('Threshold = {}'.format(threshold))

        dist_path_tuples = list(zip(distances, npy_path_list))
        print('With outliers {} items'.format(len(dist_path_tuples)))

        no_outliers_paths = remove_outliers(dist_path_tuples, threshold)
        print('Without outliers {} items'.format(len(no_outliers_paths)))
        most_different_paths = compute_most_different_images(no_outliers_paths, N)
        
        print('Most different {} items'.format(len(most_different_paths)))
        to_remove = set(npy_path_list) - set(most_different_paths)

        print('Deleting {} items'.format(len(to_remove)))
        for to_rem in to_remove:
            os.remove(to_rem)
            os.remove(utils.png_path_from_npy_path(to_rem))

        #im = Image.fromarray(avg_img * 255.0)
        #im = im.convert('L')
        #im.save('avg_{}.png'.format(cat))
