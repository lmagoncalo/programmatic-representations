from glob import glob
from shutil import copy2
import os


def copy_folder(from_dir, dest):
    files = glob(from_dir + '/*')
    os.makedirs(dest)

    for file_ in files:
        copy2(file_, dest)


def get_best(n, directories, output_dir):
    for direc in directories:
        folder_name = direc.split('/')[-1]
        os.makedirs(output_dir + '/' + folder_name)

        stat_files = glob(direc + '/fitness/pop*.csv')

        for gen in range(len(stat_files)):
            os.makedirs(output_dir + '/' + folder_name + '/pop' + str(gen))

        for stat_file in stat_files:
            f = open(stat_file, 'r')
            file_content = f.readlines()[1:]

            for idx in range(0, n):
                file_name = file_content[idx].split(',')[0]
                file_name = file_name.split('.')[0]

                fitness_value = file_content[idx].split(',')[-2].strip()

                gen = int(file_name.split('_')[1])
                ind = int(file_name.split('_')[2])

                dir_to_copy = direc + '/pop' + str(gen) + '/ind' + str(ind)

                copy_folder(dir_to_copy, output_dir + '/' + folder_name + '/pop' + str(gen) + '/ind' + str(
                    ind) + "_" + fitness_value)


for directory_path in ["CLIP_sunset,_bright_colors", "CLIP_hot_air_balloon", "CLIP_smiley"]:
    runs_list = list()
    for folder_name in os.listdir(directory_path):
        folder_path = os.path.join(directory_path, folder_name)

        # Check if it starts with 'run_' and is a directory
        if folder_name.startswith("run_") and os.path.isdir(folder_path):
            # print(folder_path)
            runs_list.append(folder_path)

    get_best(5, runs_list, directory_path + '/best_individuals')


