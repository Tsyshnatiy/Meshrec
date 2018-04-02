import os
import shutil

import numpy as np
from PIL import Image

from cylinder_projection import CylinderProjection

def normalize(data):
    mins = np.min(data)
    maxs = np.max(data)
    return (data - mins) / (maxs - mins)

def build_panoramic_view_and_save(path, result_path):
    cylinder_proj = CylinderProjection(path, 64, 160).projection
    cylinder_proj = normalize(cylinder_proj)

    filename = os.path.basename(path)
    npy_path = result_path + os.path.sep + os.path.splitext(filename)[0] + '.npy'
    np.save(npy_path, cylinder_proj)
    
    im = Image.fromarray(cylinder_proj * 255.0)
    im = im.convert('L')

    png_path = result_path + os.path.sep + os.path.splitext(filename)[0] + '.png'
    im.save(png_path)

def build_panoramic_views(path, result_path):
    for (_, _, filenames) in os.walk(path):
        i = 0
        for filename in filenames:
            try:
                build_panoramic_view_and_save(path + os.sep + filename, result_path)
            # Eat all exceptions
            except Exception as e:
                print('Error while processing {}: {}'.format(filename, str(e)))

            if i % 100 == 0:
                print('Processed {}/{} files'.format(i, len(filenames)))

            i += 1
        print('Processed {}/{} files'.format(len(filenames), len(filenames)))


def build_dataset(root_dir, result_dir):
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir, ignore_errors=True)

    os.mkdir(result_dir)
    
    dirs = [ name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name)) ]
    
    for dir in dirs:
        subfolders = [f.name for f in os.scandir(root_dir + os.sep + dir) if f.is_dir()]
        for subfolder in subfolders:
            inp_dir = root_dir + os.sep + dir + os.sep + subfolder
            out_dir = result_dir + os.sep + dir + os.sep + subfolder
            os.makedirs(result_dir + os.sep + dir + os.sep + subfolder)

            print('Processing files from {}'.format(inp_dir))
            build_panoramic_views(inp_dir, out_dir)


def main(source, dest = None):
    debug = False

    if dest:
        build_dataset(source, dest)
        return

    # Debug mode
    build_panoramic_view_and_save(source, '.')
    import trimesh
    mesh = trimesh.load_mesh(source)
    mesh.show()


if __name__ == '__main__':
    import sys
    args_num = len(sys.argv)
    
    if args_num == 2:
        main(sys.argv[1])
    elif args_num == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        raise ValueError('Invalid args number')
