import configparser
import logging

class RandomGeneratorConfig:
	"""Class responsible for the management of the initial population parametrization"""

	def __init__(self, dir_cfg):
		self.config_directory = dir_cfg
		self.color_values = dict()
		self.geometric_values = dict()
		self.num_rules=0
		self.max_depth=0

		self.logging = "logger.log"
		logging.basicConfig(filename=self.logging,level=logging.DEBUG)

	def ConfigSectionMap(self, section, config):
		"""Function that fetches a value from the config file"""

		dict1 = {}
		options = config.options(section)
		for option in options:
			try:
				dict1[option] = config.get(section, option)
				if dict1[option] == -1:
					logging.debug("Error: configure_random.py/ConfigSectionMap/try: "+option)
			except:
				logging.debug("Error: configure_random.py/ConfigSectionMap/except: "+option)
				dict1[option] = None
		return dict1

	def getParametersName(self, sectionName):
		"""Function that returns all the parameters names of a given section"""

		f = open(self.config_directory,'r')
		f_c = f.readlines()
		f.close()
		parameters_list=list()

		section = False
		for line in f_c:
			if line[0] == '[':
				section = False
				section_name = line.replace('[','').replace(']','').replace(' ','').replace('\n','')
				if sectionName == section_name:
					section = True
			elif section:
				parameter_name = line.split(':')[0].replace(' ','').replace('\n','')
				if parameter_name != '':
					parameters_list.append(parameter_name)

		
		return parameters_list

	def readCfgFile(self):
		config = configparser.ConfigParser()
		config.read(self.config_directory)

		try:
			#Color Parameters
			color_parameters=self.getParametersName('ColorParameters')
			for param in color_parameters:
				self.color_values.update({param: eval(self.ConfigSectionMap("ColorParameters",config)[param])})	
			
			#Geometric Parameters
			geometric_parameters=self.getParametersName('GeometricParameters')
			for param in geometric_parameters:
				self.geometric_values.update({param: eval(self.ConfigSectionMap("GeometricParameters",config)[param])})
			
			#Other Parameters
			self.max_shape_rules = float(self.ConfigSectionMap("Other",config)['max_shape_rules'])
			self.rule_repetition = float(self.ConfigSectionMap("Other",config)['rule_repetition'])
			self.terminal_prob = float(self.ConfigSectionMap("Other",config)['terminal_probability'])
			self.color_param_prob = float(self.ConfigSectionMap("Other",config)['color_param_probability'])
			self.geometric_param_prob = float(self.ConfigSectionMap("Other",config)['geometric_param_probability'])
			self.background_prob = float(self.ConfigSectionMap("Other",config)['background_probability'])
			self.rule_name_length = int(self.ConfigSectionMap("Other",config)['rule_name_length'])
			self.num_rules = int(self.ConfigSectionMap("Other",config)['num_rules'])
			self.max_depth = int(self.ConfigSectionMap("Other",config)['max_depth'])

		except Exception as e:
			logging.debug("Error: configure_random.py/readCfgFile/except: Error reading config file: "+self.config_directory)
			exit(0)


class RandomGenerator:
	def __init__(self, dir_cfg):
		self.parameters = RandomGeneratorConfig(dir_cfg)
		self.parameters.readCfgFile()
