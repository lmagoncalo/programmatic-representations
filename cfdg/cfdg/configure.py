import configparser
import logging

class Config:
	"""Class responsible for the management of the engine's parametrization"""

	def __init__(self, dir_cfg):
		self.config_directory=dir_cfg

		self.initial_pop_directory=None
		self.output_directory=None

		self.num_runs=None
		self.num_generations=None
		self.pop_size=None

		self.tournament_size=None
		self.fitness_function=None
		self.other_fitnesses=None
		self.elite_size=None

		self.crossover_probability=None

		self.mutation_startshape=None

		self.mutation_background_rename=None
		self.mutation_background_value=None
		self.mutation_background_mu=None
		self.mutation_background_std=None

		self.mutation_parameter_rename=None
		self.mutation_parameter_remove=None
		self.mutation_parameter_value=None
		self.mutation_parameter_mu=None
		self.mutation_parameter_std=None

		self.mutation_rule_duplicate=None
		self.mutation_rule_remove=None
		self.mutation_rule_copyRename=None

		self.mutation_symbol_remove=None
		self.mutation_symbol_replace=None
		self.mutation_symbol_add=None
		self.seeds = None
		self.contextfree_seed = None
		self.rendering_time = None
		self.max_renderer = None

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
					logging.debug("Error: configure.py/ConfigSectionMap/try: "+option)
			except:
				logging.debug("Error: configure.py/ConfigSectionMap/except: "+option)
				dict1[option] = None
		return dict1

	def readCfgFile(self):
		config = configparser.ConfigParser()
		config.read(self.config_directory)

		try:		

			#section: Directories
			self.initial_pop_directory= eval(self.ConfigSectionMap("Directories",config)['initial_pop'])
			self.output_directory= self.ConfigSectionMap("Directories",config)['output']

			#section: Secection
			self.tournament_size=int(self.ConfigSectionMap("Selection",config)['tournament_size'])
			self.fitness_function=[palavra.replace(' ','') for palavra in self.ConfigSectionMap("Selection",config)['fitness_function'].replace(' ','').split(',')]
			self.other_fitnesses= [palavra.replace(' ','') for palavra in self.ConfigSectionMap("Selection",config)['other_fitnesses'].replace(' ','').split(',')]
			self.elite_size=int(self.ConfigSectionMap("Selection",config)['elite_size'])

			#section: Crossover
			self.crossover_probability=float(self.ConfigSectionMap("Crossover",config)['crossover_probability'])

			#section: Mutations
			self.mutation_startshape= float(self.ConfigSectionMap("Mutations",config)['startshape'])

			self.mutation_background_rename= float(self.ConfigSectionMap("Mutations",config)['background_rename'])
			self.mutation_background_value= float(self.ConfigSectionMap("Mutations",config)['background_value'])
			self.mutation_background_mu= float(self.ConfigSectionMap("Mutations",config)['background_mu'])
			self.mutation_background_std= float(self.ConfigSectionMap("Mutations",config)['background_std'])

			self.mutation_parameter_rename= float(self.ConfigSectionMap("Mutations",config)['parameter_rename'])
			self.mutation_parameter_remove= float(self.ConfigSectionMap("Mutations",config)['parameter_remove'])
			self.mutation_parameter_value= float(self.ConfigSectionMap("Mutations",config)['parameter_value'])
			self.mutation_parameter_mu= float(self.ConfigSectionMap("Mutations",config)['parameter_mu'])
			self.mutation_parameter_std= float(self.ConfigSectionMap("Mutations",config)['parameter_std'])

			self.mutation_rule_duplicate= float(self.ConfigSectionMap("Mutations",config)['rule_duplicate'])
			self.mutation_rule_remove= float(self.ConfigSectionMap("Mutations",config)['rule_remove'])
			self.mutation_rule_copyRename= float(self.ConfigSectionMap("Mutations",config)['rule_copy_and_rename'])

			self.mutation_symbol_remove= float(self.ConfigSectionMap("Mutations",config)['symbol_remove'])
			self.mutation_symbol_replace= float(self.ConfigSectionMap("Mutations",config)['symbol_replace'])
			self.mutation_symbol_add= float(self.ConfigSectionMap("Mutations",config)['symbol_add'])
		
			#section: Other
			self.num_runs= int(self.ConfigSectionMap("Other",config)['num_runs'])
			self.num_generations= int(self.ConfigSectionMap("Other",config)['num_generations'])
			self.pop_size= int(self.ConfigSectionMap("Other",config)['pop_size'])
			self.seeds = eval(self.ConfigSectionMap("Other",config)['seeds'])
			self.contextfree_seed = eval(self.ConfigSectionMap("Other",config)['contextfree_seed'])
			self.rendering_time = eval(self.ConfigSectionMap("Other",config)['rendering_time'])
			self.max_renderer = self.ConfigSectionMap("Other",config)['max_renderer']



		except Exception as err:
			print("Error: configure.py/readCfgFile/except: Error reading config file: "+self.config_directory)
			logging.debug("Error: configure.py/readCfgFile/except: Error reading config file: "+self.config_directory)
			exit(0)

