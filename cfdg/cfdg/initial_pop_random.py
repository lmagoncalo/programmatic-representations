from configure_random import RandomGenerator
import string
import random
from structure import PopMember, Rule, Node, Parameter
import fitness 
import os

from mutation import check_member_validity

class InitialPopGenerator:
	"""Class responsible for the generation of a single individual"""

	def __init__(self, dir_cfg):
		self.parameters = RandomGenerator(dir_cfg).parameters
		self.rules = self.generateRuleNames(self.parameters.num_rules, self.parameters.rule_name_length)
		self.terminals = ['CIRCLE', 'SQUARE', 'TRIANGLE']
		self.num_parameters = {'hue':[1], 'saturation':[1], 'brightness':[1], 'alpha':[1], 'rotate':[1], 'size':[1], 'x':[1],'y':[1],'z':[1],'flip':[1],'skew':[2]}

	def getAllParameters(self):
		return self.parameters.color_values.keys()+self.parameters.geometric_values.keys()


	def generateRuleNames(self, num_rules, rule_length):
		chars = string.ascii_uppercase+string.ascii_lowercase
		rules = []

		for i in range(num_rules):
			rules.append(''.join(random.choice(chars) for x in range(rule_length)))

			num_repetitions = random.randint(1,self.parameters.rule_repetition+1)

			for j in range(1, num_repetitions):
				rules.append(rules[len(rules)-1])
			
		return rules


	def buildStartshape(self, rules):
		return random.choice(rules)


	def buildPopMember(self):
		self.pop_member = PopMember()

		#startshape
		self.pop_member.startshape = self.buildStartshape(self.rules)

		#background
		if self.parameters.background_prob < random.random():
			self.pop_member.background = self.generateBackground()
		else:
			self.pop_member.background = None

		#rules
		self.generateRules(self.rules)

		#set probabilities to between 0 and 1
		total_probabilities = 0.0
		for rule in self.pop_member.rule_list:
			total_probabilities +=rule.probability

		for rule in self.pop_member.rule_list:
			rule.probability = rule.probability/total_probabilities


		return self.pop_member


	def generateBackground(self):
		background_node = Node()

		for param in self.parameters.color_values.keys():
			if random.random() < self.parameters.color_param_prob:
				parameter = Parameter()
				parameter.name = param

				parameter_range = self.parameters.color_values[param]
				parameter.values.append(random.uniform(parameter_range[0],parameter_range[1]))

				background_node.parameters.append(parameter)

		return background_node


	def generateRules(self, rules):

		for rule_name in rules:
			rule = Rule()
			rule.name = rule_name
			rule.probability = random.randint(1,100)

			num_rules = random.randint(1, self.parameters.max_shape_rules+1)

			for it in range(0,num_rules):
				node = Node()

				#terminal
				if random.random() < self.parameters.terminal_prob:
					terminal = random.choice(self.terminals)
					node.name = terminal

				#non terminal
				else:
					node.name = random.choice(self.rules)

				node.parameters = self.generateProperties()
				rule.node_list.append(node)
					
			self.pop_member.rule_list.append(rule)


	def generateProperties(self):

		parameters = []

		for param in self.parameters.color_values.keys():
			if random.random() < self.parameters.color_param_prob:
				parameter = Parameter()
				parameter.name = param

				parameter_range = self.parameters.color_values[param]
				num_param = random.choice(self.num_parameters[param])

				for value in range(0, num_param):
					parameter.values.append(random.uniform(parameter_range[0],parameter_range[1]))

				parameters.append(parameter)

		for param in self.parameters.geometric_values.keys():
			if random.random() < self.parameters.geometric_param_prob:
				parameter = Parameter()
				parameter.name = param

				parameter_range = self.parameters.geometric_values[param]
				num_param = random.choice(self.num_parameters[param])

				for value in range(0, num_param):
					parameter.values.append(random.uniform(parameter_range[0],parameter_range[1]))

				parameters.append(parameter)

		return parameters


				


def generateInitialPopulation(output_dir, fitness_function, num_members, run_number, context_free_seed, python_seed, max_renderer, render_time, prompt, pop_scale_factor=3):
	"""Function that generates a whole new population"""

	initial_pop = []

	random.seed(python_seed)

	for member in range(pop_scale_factor*num_members):
		
		pop_generator = InitialPopGenerator('./random_generator.cfg')
		member_output = pop_generator.buildPopMember()

		if not check_member_validity(member_output):
			print("deu merda")

		f_out = open(output_dir+'/random_init_'+str(member)+'.cfdg', 'w')
		f_out.write(member_output.printMember())
		f_out.close()

		fitness.renderGrammar(member_output, output_dir+'/random_init_'+str(member)+'.cfdg',output_dir+'/random_init_'+str(member)+'.png', context_free_seed,rendering_time=render_time,max_generations = max_renderer)

		member_output.fileName = output_dir+'/random_init_'+str(member)+'.cfdg'		

		initial_pop.append(member_output)
	
	
	fitness.classifyFitness(initial_pop, fitness_function, True, prompt)

	initial_pop.sort(key=lambda x: x.fitness, reverse=True)

	for member in initial_pop[:num_members]:
		os.rename(member.fileName, member.fileName.split(".cfdg")[0]+'_#'+str(member.fitness)+'.cfdg')
		member.fileName = member.fileName.split(".cfdg")[0]+'_#'+str(member.fitness)+'.cfdg'

	return initial_pop[:num_members]