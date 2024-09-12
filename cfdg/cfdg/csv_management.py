import csv

def write_content(fileName, data, assure_new=True, multiple=False):
	"""Function that writes content in csv format
	assure_new - replaces fileName if it exists, else just appends
	multiple - if multiple lines to write are provided. In this case the data variable is a list"""

	if assure_new:
		permissions = 'w'
	else:
		permissions = 'a+w'

	with open(fileName, permissions) as myfile:
		wr = csv.writer(myfile)

		if(not multiple):
			wr.writerow(data.encode())

		else:
			print(data)
			for x in range(len(data)):
				print(data[x])
				wr.writerow(data[x])

	myfile.close()


def read_content(fileName):
	f = open(fileName)
	lines_content = f.readlines()

	for line in range(len(lines_content)):
		lines_content[line] = lines_content[line].replace('\r\n','').split(',')

	return lines_content
