import os

folders = {'table', 'dresser', 'toilet', 'monitor', 'chair'}
start_indices = {
    'table' : 493,
    'dresser' : 287,
    'toilet' : 445,
    'monitor' : 566,
    'chair' : 990
}

def convert(source_dir, dest_dir):
    def call_converter(from_path, to_path):
        import subprocess

        cmd = 'SkpOffConverter.exe' + ' ' + '"' + from_path + '"' + ' ' + to_path

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (result, error) = process.communicate()

        rc = process.wait() 

        if rc != 0:
            print('Error: {} failed to execute command: {}'.format(error, cmd))
        return result

    def do_convert(cur_folder, source_file, destination):
        name = cur_folder + '_' + str(start_indices[cur_folder]) + '.off'
        dest_file = destination + os.sep + name
        print('Converting to {}'.format(dest_file))
        call_converter(source_file, dest_file)
    
    def convert_files(cur_folder, prefix, files, destination):
        for file in files:
            old_path = prefix + os.sep + file
            if os.path.isfile(old_path) and file.endswith('skp'):
                do_convert(cur_folder, prefix + os.sep + file, destination)
                new_name = cur_folder + '_' + str(start_indices[cur_folder])
                os.rename(old_path, prefix + os.sep + new_name + '.skp')
                start_indices[cur_folder] += 1

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for folder in folders:
        dest = dest_dir + os.sep + folder
        os.makedirs(dest)

        dir = source_dir + os.sep + folder

        files = os.listdir(dir)
        convert_files(folder, dir, files, dest)

if __name__ == "__main__":
    import sys
    convert(sys.argv[1], sys.argv[2])