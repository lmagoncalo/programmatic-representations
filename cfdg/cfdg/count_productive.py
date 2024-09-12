def count_productive_total(member):

	total_rules = []

	for rule in member.rule_list:
		if rule.name not in total_rules:
			total_rules.append(rule.name)

	productive_rules = get_productive(member)

	output = list()

	#output = [productive_rules, unproductive_rules, productive_percentage, unproductive_percentage]
	output = [len(productive_rules), len(member.rule_list)-len(productive_rules)]

	if len(total_rules)>0:
		output.extend([float(float(len(productive_rules))/float(len(member.rule_list))), float(float(len(member.rule_list)-len(productive_rules))/float(len(member.rule_list)))])
	else:
		output.extend([0,0])

	return output


def get_productive(member):
	productive = []
	terminals = ['SQUARE','TRIANGLE', 'CIRCLE']

	#add rules with terminals
	get_terminal_rules(productive, terminals, member)

	while(True):
		size = len(productive)
		get_reachable_terminal(productive, terminals, member)

		new_size = len(productive)

		if(size == new_size):
			break

		size = new_size

	return productive


def get_terminal_rules(productive, terminals, member):

	for rule in member.rule_list:
		for node in rule.node_list:
			if node.name in terminals and rule not in productive:
				productive.append(rule)


def get_reachable_terminal(productive, terminals, member):

	rules_name = [rule.name for rule in productive]

	for rule in member.rule_list:
		for node in rule.node_list:
			if node.name in rules_name and rule not in productive and node.name not in terminals:
				productive.append(rule)


def erase_unproductive(member):
	productive_rules = get_productive(member)
	unproductive_rules = list()
	unproductive_names = list()

	for rule in member.rule_list:
		if rule not in productive_rules:
			unproductive_rules.append(rule)

	unproductive_names = [rule.name for rule in unproductive_rules]

	while(len(unproductive_rules)>0):
		remove_rule = unproductive_rules.pop()

		for rule_idx in range(len(member.rule_list)):
			if member.rule_list[rule_idx] == remove_rule:
				del member.rule_list[rule_idx]
				break

	member.setDifferentRules()

	del_items = list()
	for rule in member.rule_list:
		for node_idx in range(len(rule.node_list)):
			if rule.node_list[node_idx].name in unproductive_names and rule.node_list[node_idx].name not in member.getDifferentRules():
				del_items.append(node_idx)

		while(len(del_items)>0):
			del rule.node_list[del_items.pop()]