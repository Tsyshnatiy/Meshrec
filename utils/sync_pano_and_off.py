import os
import glob
import shutil

def reject_extension(filename):
    return filename[:filename.rfind('.')]

def take_filename(path):
    return os.path.basename(path)

def fname(path):
    return reject_extension(take_filename(path))
    
def create_dir_recursively(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

def move(src, dst):
    if os.path.dirname(dst):
        create_dir_recursively(os.path.dirname(dst))
    
    try:
        shutil.move(src, dst)
        print('Moved {} to {}'.format(src, dst))
    except FileNotFoundError:
        pass

def remove_empty_folders(path, remove_root=True):
    'Function to remove empty folders'
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                remove_empty_folders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and remove_root:
        print('Removing empty folder: {}'.format(path))
        os.rmdir(path)

def sync(pano_path, off_path):
    pano_wildcard = pano_path + os.sep + '**' + os.sep + '*.png'
    off_wildcard = off_path + os.sep + '**' + os.sep + '*.off'
    
    pano_path_list = glob.glob(pano_wildcard, recursive=True)
    off_path_list = glob.glob(off_wildcard, recursive=True)
    
    pano_file_list = [fname(f) for f in pano_path_list]
    off_file_list = [fname(f) for f in off_path_list]
    
    for i in range(len(pano_file_list)):
        pano_name = pano_file_list[i]
        pano_file_path = pano_path_list[i]

        off_should_be_at = off_path + pano_file_path[len(pano_path):]
        off_should_be_at = reject_extension(off_should_be_at) + '.off'
        
        off_now_at = [f for f in off_path_list if f.find(pano_name) != -1][0]

        if off_should_be_at != off_now_at:
            move(off_now_at, off_should_be_at)
    
    for off in off_path_list:
        off_filename = fname(off)
        if not off_filename in pano_file_list:
            print('Removing {}'.format(off))
            os.remove(off)
  
    remove_empty_folders(off_path)

if __name__ == "__main__":
    import sys
    sync(sys.argv[1], sys.argv[2])