import lexer
from glob import glob
from csv_management import write_content

def open_initial_pop_member(file_location):
	f_in = open(file_location,'r')
	fileContent = f_in.readlines()
	f_in.close()
	
	_str=""
	for line in fileContent:
		_str+=line.replace(' ','  ').replace('\n','  ').replace('\r','  ').replace('\t','  ').replace('{','{ ').replace('}',' }')

	pop_member=lexer.newMember(_str)
	pop_member.setDifferentRules()
	pop_member.classifyNodes()
	pop_member.fileName = file_location

	return pop_member


def open_dir(dir_path):
	files_list = glob(dir_path+'*.cfdg')
	pop = [open_initial_pop_member(file_path) for file_path in files_list]

	return pop


def count_useless_rules(member):
	total_rules = list()

	#count total rules
	for rule in member.rule_list:
		if rule.name not in total_rules:
			total_rules.append(rule.name)

	#get reachable rules
	reachable_rules=list()
	reachable_rules = count_recursive_rules(reachable_rules, member, member.startshape)

	reachable_total = list()
	unreachable_total = list()

	for rule in member.rule_list:
		if rule.name in reachable_rules:
			reachable_total.append(rule.name)
		else:
			unreachable_total.append(rule.name)


	try:
		return [len(member.rule_list), len(total_rules), len(reachable_total), len(unreachable_total), len(reachable_rules), len(total_rules)-len(reachable_rules), float(len(reachable_total))/float(len(member.rule_list)), float(len(unreachable_total))/float(len(member.rule_list)), float(len(reachable_rules))/float(len(total_rules)), float(len(total_rules)-len(reachable_rules))/float(len(total_rules))]
	except ZeroDivisionError:
		return [len(member.rule_list), len(total_rules), len(reachable_total), len(unreachable_total), len(reachable_rules), len(total_rules)-len(reachable_rules), 0, 0, 0, 0]


def count_recursive_rules(reachable_rules, member, current_node):
	count_recursive__rules(reachable_rules, member, current_node)

	found = False
	for rule in member.rule_list:
		if rule.name == member.startshape:
			found=True
			break

	if found is False:
		reachable_rules = list()

	return reachable_rules


def count_recursive__rules(reachable_rules, member, current_node):
	if current_node not in reachable_rules:
		reachable_rules.append(current_node)

	number_of_calls=0

	for rule in member.rule_list:
		if rule.name == current_node:
			for node in rule.node_list:
				number_of_calls += 1
				if node.name != 'SQUARE' and node.name != 'CIRCLE' and node.name != 'TRIANGLE' and node.name not in reachable_rules:
					count_recursive__rules(reachable_rules, member, node.name)

	if number_of_calls == 0:
		reachable_rules.remove(current_node)



def remove_useless_symbols(pop_member):
	reachable_rules=list()
	count_recursive_rules(reachable_rules, pop_member, pop_member.startshape)

	indexes_to_remove = list()

	for index in range(len(pop_member.rule_list)):
		if pop_member.rule_list[index].name not in reachable_rules:
			indexes_to_remove.append(index)

	indexes_to_remove.sort(reverse=True)

	for index in indexes_to_remove:
		del pop_member.rule_list[index]