from random import random, choice, gauss, randint, getstate, setstate, uniform
from string import ascii_uppercase, ascii_lowercase
from copy import deepcopy
from structure import *
from configure_random import RandomGenerator

def check_member_validity(member):
	total_rules = ['CIRCLE', 'SQUARE', 'TRIANGLE']

	for rule in member.rule_list:
		if rule.name not in total_rules:
			total_rules.append(rule.name)

	for rule in member.rule_list:
		for node in rule.node_list:
			if node.name not in total_rules:
				return False

	return True


#returns seed state
def mutation(pop_member, prob_startshape_mutation, prob_background_parameter_rename_mutation, prob_background_parameter_value_mutation, prob_parameter_background_change_mutation_mu,
	prob_parameter_background_change_mutation_std, prob_parameter_rename_mutation, prob_parameter_remove_mutation, prob_parameter_value_mutation, prob_parameter_change_mutation_mu,
	prob_parameter_change_mutation_std, prob_duplicate_rule, prob_remove_rule, prob_copy_rename_rule, prob_remove_symbol, prob_replace_symbol, prob_add_symbol, seed_state, dir_cfg='./random_generator.cfg'):

	parameters_possible = RandomGenerator(dir_cfg).parameters

	setstate(seed_state)

	if len(pop_member.getDifferentRules()) == 0:
		return getstate()

	#//////////////////////////////////////
	#---------Startshape Mutation----------
	#//////////////////////////////////////

	if random() < prob_startshape_mutation:
		different_rules = pop_member.getDifferentRules()
		pop_member.startshape = choice(different_rules)


	#//////////////////////////////////////
	#---------Background Mutations---------
	#//////////////////////////////////////

	all_possible_background_parameters=list(parameters_possible.color_values.keys())
	parameters_del = list()


	if pop_member.background is not None:
		for parameter_idx in range(len(pop_member.background.parameters)):
			#Change parameter name
			if random() < prob_background_parameter_rename_mutation:
				pop_member.background.parameters[parameter_idx].name = choice(all_possible_background_parameters)
			
			#Change parameter value
			for i in range(len(pop_member.background.parameters[parameter_idx].values)):
				if random() < prob_background_parameter_value_mutation:
					pop_member.background.parameters[parameter_idx].values[i]+=gauss(prob_parameter_background_change_mutation_mu,prob_parameter_background_change_mutation_std)

					#assure that the parameter values stays legal
					pop_member.background.parameters[parameter_idx].values[i]=max(pop_member.background.parameters[parameter_idx].values[i], parameters_possible.color_values[pop_member.background.parameters[parameter_idx].name][0])
					pop_member.background.parameters[parameter_idx].values[i]=min(pop_member.background.parameters[parameter_idx].values[i], parameters_possible.color_values[pop_member.background.parameters[parameter_idx].name][1])



			#Remove parameter
			if(len(pop_member.background.parameters)>0 and random() < prob_parameter_remove_mutation):
				parameters_del.append(parameter_idx)

		while len(parameters_del) > 0:
			del pop_member.background.parameters[parameters_del.pop()]




	#//////////////////////////////////////
	#----------Parameter Mutations---------
	#//////////////////////////////////////

	#NEW TODO - num parameters fixado a 1!
	num_parameters = {'hue':[1], 'saturation':[1], 'brightness':[1], 'alpha':[1], 'rotate':[1], 'size':[1], 'x':[1],'y':[1],'z':[1],'flip':[1],'skew':[2]}

	for rule in pop_member.rule_list:
		for node in rule.node_list:
			for parameter_idx in range(len(node.parameters)):
				#Change parameter name
				if random() < prob_parameter_rename_mutation:
					numero_parametros = len(node.parameters[parameter_idx].values)

					possible_to_choose = list()
					for var in num_parameters.keys():
						for num_param in num_parameters[var]:
							if num_param == numero_parametros:
								possible_to_choose.append(var)

					node.parameters[parameter_idx].name = choice(possible_to_choose)

				#Change parameter value
				for i in range(len(node.parameters[parameter_idx].values)):
					if random() < prob_parameter_value_mutation:
						node.parameters[parameter_idx].values[i]+=gauss(prob_parameter_change_mutation_mu,prob_parameter_change_mutation_std)

				#Remove parameter
				if len(node.parameters)>0 and random() < prob_parameter_remove_mutation:
					parameters_del.append(parameter_idx)

			#Remove parameter
			while len(parameters_del) > 0:
				del node.parameters[parameters_del.pop()]


	#//////////////////////////////////////
	#------------Rule Mutations------------
	#//////////////////////////////////////

	#Duplicate rule
	for i in range(len(pop_member.rule_list)):
		if random() < prob_duplicate_rule:
			duplicate = deepcopy(pop_member.rule_list[i])
			pop_member.rule_list.append(duplicate)


	#Remove rule
	rename_startshape = False

	del_items=[]
	del_items_name = []

	for i in range(len(pop_member.rule_list)):

		num_rules = len(pop_member.rule_list) - len(del_items)

		if num_rules >1 and random() < prob_remove_rule:	
			del_items.append(i)
			if(pop_member.rule_list[i].name not in del_items_name):
				del_items_name.append(pop_member.rule_list[i].name)

			if pop_member.startshape == pop_member.rule_list[i].name:
				rename_startshape = True

	del_items.sort()

	while (len(del_items)>0):
		del pop_member.rule_list[del_items.pop()]	

	pop_member.setDifferentRules()

	#remove links of the deleted rules
	for rule in pop_member.rule_list:
		for node_idx in range(len(rule.node_list)):
			if rule.node_list[node_idx].name in del_items_name and rule.node_list[node_idx].name not in pop_member.getDifferentRules():
				del_items.append(node_idx)

		del_items.sort()
		while(len(del_items)>0):
			del rule.node_list[del_items.pop()]

	if rename_startshape:
		if pop_member.startshape not in pop_member.getDifferentRules() and len(pop_member.getDifferentRules())>0:
			pop_member.startshape = choice(pop_member.getDifferentRules())



	#//////////////////////////////////////
	#-----------Symbol Mutations-----------
	#//////////////////////////////////////
	for rule in pop_member.rule_list:
		del_items = []
		for i in range(len(rule.node_list)):
			#remove symbol
			if random() < prob_remove_symbol:
				del_items.append(i)

			#replace symbol
			dif_rules = pop_member.getDifferentSymbols()
			if random() < prob_replace_symbol:
				rule.node_list[i].name = choice(dif_rules)

		del_items.sort()

		for x in range(len(del_items)):
			del rule.node_list[del_items.pop()]	


		#add symbol
		if random() < prob_add_symbol:
			#create and link new rule
			node_name = create_new_rule(pop_member)
			node = Node()
			node.setName(node_name)
			if(len(rule.node_list)>0):
				rule.node_list.insert(randint(0,len(rule.node_list)-1), node)
			else:
				rule.node_list.append(node)


	return getstate()


#//////////////////////////////////////
#---------Random Rule Creation---------
#//////////////////////////////////////

def create_new_rule(pop_member, rule_length=5, max_number_nodes=3):
	

	rule = Rule()
	chars = ascii_uppercase+ascii_lowercase
	rule_name = ''.join(choice(chars) for x in range(rule_length))
	rule.name = rule_name
	rule.probability = randint(1,100)

	for it in range(0,randint(1,max_number_nodes)):
		node = Node()

		#terminal
		if random() < 0.5:
			node.name = choice(['CIRCLE', 'SQUARE', 'TRIANGLE'])

		#non terminal
		else:
			node.name = choice(pop_member.getDifferentRules())

		node.parameters = generateProperties()
		rule.node_list.append(node)

	pop_member.rule_list.append(rule)
	pop_member.setDifferentRules()

	return rule_name


def generateProperties(dir_cfg='./random_generator.cfg'):

	loaded_parameters = RandomGenerator(dir_cfg).parameters
	num_parameters = {'hue':[1], 'saturation':[1], 'brightness':[1], 'alpha':[1], 'rotate':[1], 'size':[1], 'x':[1],'y':[1],'z':[1],'flip':[1],'skew':[2]}

	parameters = []

	for param in loaded_parameters.color_values.keys():
		if random() < loaded_parameters.color_param_prob:
			parameter = Parameter()
			parameter.name = param

			parameter_range = loaded_parameters.color_values[param]
			num_param = choice(num_parameters[param])

			for value in range(0, num_param):
				parameter.values.append(uniform(parameter_range[0],parameter_range[1]))

			parameters.append(parameter)


	for param in loaded_parameters.geometric_values.keys():
		if random() < loaded_parameters.geometric_param_prob:
			parameter = Parameter()
			parameter.name = param

			parameter_range = loaded_parameters.geometric_values[param]
			num_param = choice(num_parameters[param])

			for value in range(0, num_param):
				parameter.values.append(uniform(parameter_range[0],parameter_range[1]))

			parameters.append(parameter)

	return parameters


	