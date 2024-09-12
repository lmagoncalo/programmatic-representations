import os
import subprocess
import time

class Command:
	"""Class responsible for the execution of programs outside python environment"""

	def __init__(self, cmd, timeout):

		self.cmd = cmd
		self.pid = None

		#get output filename that follows -o in the cfdg speficication
		file_name = self.cmd.split('-o')[1].strip().split(" ")[0]
		#file_name = self.cmd.split('-o')[1].split(' -')[0].replace(' ','')

		#create file to prevent image not rendering
		open(file_name, 'w').close()

		with open(os.devnull, "w") as fnull:
			self.process = subprocess.Popen("exec "+self.cmd,shell=True,stdout = fnull, stderr = fnull)
			self.pid = self.process.pid
		self.run(timeout)


	def run(self, timeout):
		if timeout is not None:
			timeout = float(timeout)
			start = time.time()
			end = start+timeout
			interval = min(timeout / 1000.0, .25)
		else:
			interval = min(3/1000, 0.25)



		while True:
			result = self.process.poll()
			if result is not None:
				return result

			if timeout is not None and time.time() >= end:
				break

			time.sleep(interval)
		
		self.process.kill()
