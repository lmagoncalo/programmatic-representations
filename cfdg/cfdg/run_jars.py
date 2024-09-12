import subprocess
import random
from sys import maxsize

def run_frac_lac(fitness_function, files_list, csv_path, del_file = False, objective_value=1.5):
	list_of_files=''
	fitness_list = list() 

	random_number = random.randint(0, maxsize)
	csv_path = csv_path.split('.csv')[0]+str(random_number)+'.csv'

	for name in files_list:
		list_of_files +=' '+name
	
	subprocess.getstatusoutput('java -jar FracLacFitness.jar -bw -'+fitness_function+' '+list_of_files+' -out '+csv_path)

	f = open(csv_path,'r')

	content = f.readlines()
	content=content[1:]
	for line in content:
		line_content = line.replace('\n','').split(',')
		
		fitness_list.append(1.0/(1.0+abs(objective_value - float(line_content[1]))))

	f.close()

	subprocess.getoutput('rm '+csv_path)

	return fitness_list



def run_aesthetic(fitness_function, files_list, output_path, del_file = False):
	list_of_files=''
	fitness_list = list() 

	random_number = random.randint(0, maxsize)
	output_path = output_path.split('.csv')[0]+str(random_number)+'.csv'

	for name in files_list:
		list_of_files +=' '+name

	subprocess.getstatusoutput('./aestheticfitness -'+fitness_function+' -out '+output_path+' '+list_of_files)

	f = open(output_path,'r')

	content = f.readlines()
	content=content[1:]
	for line in content:
		line_content = line.replace('\n','').split(',')
		
		if(fitness_function == 'bell'):
			fitness_list.append(-abs(float(line_content[1])))
		else:
			fitness_list.append(float(line_content[1]))

	f.close()

	subprocess.getoutput('rm '+output_path)

	return fitness_list

