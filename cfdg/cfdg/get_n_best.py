from glob import glob
from shutil import copy2
import os

def copy_folder(from_dir, dest):
	files = glob(from_dir+'/*')
	os.makedirs(dest)

	for file_ in files:
		copy2(file_, dest)

def get_best(n, directories, output_dir):
	for direc in directories:
		folder_name = direc.split('/')[-1]
		os.makedirs(output_dir+'/'+folder_name)

		stat_files = glob(direc+'/fitness/pop*.csv')

		for gen in range(len(stat_files)):
			os.makedirs(output_dir+'/'+folder_name+'/pop'+str(gen))

		for stat_file in stat_files:
			f = open(stat_file,'r')
			file_content = f.readlines()[1:]

			for idx in range(0,n):
				file_name = file_content[idx].split(',')[0]
				file_name = file_name.split('.')[0]

				gen = int(file_name.split('_')[1])
				ind = int(file_name.split('_')[2])

				dir_to_copy = direc+'/pop'+str(gen)+'/ind'+str(ind)

				copy_folder(dir_to_copy, output_dir+'/'+folder_name+'/pop'+str(gen)+'/ind'+str(ind))