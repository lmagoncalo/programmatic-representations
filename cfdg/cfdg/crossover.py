import lexer
import random
import copy
from structure import PopMember, Node

def crossover(A, B, prob_cross, seed_state):

	random.setstate(seed_state)

	if random.random() < prob_cross:
		(new_a, new_b) = crossover_processing(A, B)
		return (new_a, new_b, random.getstate())
	else:
		return (copy.deepcopy(A), copy.deepcopy(B), random.getstate())

def crossover_processing(A, B):
	
	#crossover point
	n_a = choose_croosover_node(A)
	n_b = choose_croosover_node(B)

	#radius
	r_a = choose_radius(A, n_a)
	r_b = choose_radius(B, n_b)

	#subgraph selection
	subgraph_a = subgraph_selection(A, n_a, r_a)
	subgraph_b = subgraph_selection(B, n_b, r_b)

	#minimum spanning tree
	mst_a = mst(A, n_a, r_a+1)
	mst_b = mst(B, n_b, r_b+1)

	#correspondence list
	correspondence_list = set_correspondence(mst_a,n_a,mst_b,n_b)

	#swap
	(new_a, new_b) = swap_nodes(A, B, subgraph_a, subgraph_b, mst_a, mst_b, correspondence_list)

	return (new_a, new_b)

def choose_croosover_node(member):
	return random.choice(member.getDifferentRules())

def choose_radius(member, node_name):
	"""Calcula a profundidade maxima e retorna um valor random entre 1 e essa profundidade"""

	global max_depth
	max_depth = 0

	def recursive(rule_list, current_node=node_name, depth=0, marked=[node_name]):
		global max_depth
		num_calls = 0
	
		depth+=1

		for rule in rule_list:
			if rule.name == current_node:
				for node in rule.node_list:
					if node.name not in marked:
						marked.append(node.name)
						recursive(rule_list, node.name, depth,  marked)
						del marked[marked.index(node.name)]
						num_calls +=1

		if num_calls == 0:
			depth -= 1

		if depth > max_depth:
			max_depth = depth

	for rule in member.rule_list:
		if rule.name == node_name:
			recursive(member.rule_list)

	return random.randint(0,max_depth)


def subgraph_selection(member, crossover_point, radius):

	subgraph = [crossover_point]

	def recursive(rule_list, subgraph, current_node = crossover_point, depth = 0, marked=[crossover_point]):
		if depth < radius:
			for rule in rule_list:
				if rule.name == current_node:
					for node in rule.node_list:
						if node.name not in marked and node.name not in ['SQUARE', 'TRIANGLE', 'CIRCLE']:
							marked.append(node.name)

							if node.name not in subgraph:
								subgraph.append(node.name)

							recursive(rule_list, subgraph, node.name, depth+1, marked)
							
							del marked[marked.index(node.name)]

	for rule in member.rule_list:
		if rule.name == crossover_point:
			recursive(member.rule_list, subgraph)

	return subgraph


def mst(member, crossover_point, radius):

	subgraph = subgraph_selection(member, crossover_point, radius)

	def find_reachable(rule_list, node_name, subgraph, already_reached):
		reachable = list()
		for rule in rule_list:
			if rule.name == node_name:
				for node in rule.node_list:
					if node.name in subgraph and node.name not in reachable and node.name not in already_reached and node.name not in ['SQUARE', 'TRIANGLE', 'CIRCLE']:
						reachable.append(node.name)

		return reachable


	reachable = [crossover_point]
	already_reached=[crossover_point]
	mst_graph = [(None, crossover_point, 0)]
	depth = 0

	while(len(already_reached) != len(subgraph)):
		depth+=1
		search_new = list()
		for node_name in reachable:
			new_reachable = find_reachable(member.rule_list, node_name, subgraph, already_reached)
			for new_reachable_node in new_reachable:
				mst_graph.append((node_name, new_reachable_node,depth))

			already_reached.extend(new_reachable)
			search_new.extend(new_reachable)
			

		reachable = copy.deepcopy(search_new)

	return mst_graph



def set_correspondence(mst_A, n_a, mst_B, n_b):

	correspondence_list = list()

	def descendants(node, mst):
		descendants_list = list()
		for tuplo in mst:
			if tuplo[0] == node and tuplo[1] not in descendants_list:
				descendants_list.append(tuplo[1])

		if len(descendants_list) == 0:
			return None

		return descendants_list


	def unmarked(desc, marked):
		unmarked_list = list()

		if desc is None:
			return None

		for elem in desc:
			if elem not in marked:
				unmarked_list.append(elem)

		if len(unmarked_list) == 0:
			return None

		return unmarked_list



	def transverse(correspondence_list, marked_A=list(), marked_B=list(), next_A=n_a, next_B=n_b):
		correspondence_list.append((next_A, next_B))

		marked_A.append(next_A)
		marked_B.append(next_B)

		while(True):

			desc_A = descendants(next_A, mst_A)
			desc_B = descendants(next_B, mst_B)

			if unmarked(desc_A, marked_A) is None and unmarked(desc_B, marked_B) is None:
				break

			if unmarked(desc_A, marked_A) is not None:
				next_a = copy.deepcopy(random.choice(unmarked(desc_A, marked_A)))

			elif desc_A is not None:
				next_a = copy.deepcopy(random.choice(desc_A))

			else:
				next_a = copy.deepcopy(next_A)


			if unmarked(desc_B, marked_B) is not None:
				next_b = copy.deepcopy(random.choice(unmarked(desc_B, marked_B)))

			elif desc_B is not None:
				next_b = copy.deepcopy(random.choice(desc_B))

			else:
				next_b = copy.deepcopy(next_B)

			transverse(correspondence_list, marked_A, marked_B, next_a, next_b)


	transverse(correspondence_list)

	return correspondence_list


def swap_nodes(A, B, subgraph_a, subgraph_b, mst_a, mst_b, correspondence_list):

	def copy_rules(subgraph_a, member_a, subgraph_b, member_b):
		new_member = PopMember()
		new_member.startshape = copy.deepcopy(member_a.startshape)
		new_member.background = copy.deepcopy(member_a.background)

		for rule_member_a in member_a.rule_list:
		 	if rule_member_a.name not in subgraph_a:
		 		new_member.rule_list.append(copy.deepcopy(rule_member_a))

		for rule_member_b in member_b.rule_list:
			if rule_member_b.name in subgraph_b:
				new_member.rule_list.append(copy.deepcopy(rule_member_b))

		return new_member


	def find_correspondence (node_name, correspondence_list):
		for tuplo in correspondence_list:
			if tuplo[0] == node_name:
				return tuplo[1]
			elif tuplo[1] == node_name:
				return tuplo[0]

		#TODO: review this (apagar os que nao estao na correspondece_list?) - confirmar que nao gera grafos desconexos
		return node_name

	def stablish_correspondence(new_member, correspondence_list, mst_a, mst_b, subgraph_a, subgraph_b):
		def last_level(subgraph):
			last = 0
			for tuplo in subgraph:
				if tuplo[2] > last:
					last = tuplo[2]
			return last

		def last_level_nodes(subgraph, last_depth):
			return_list = list()
			for tuplo in subgraph:
				if tuplo[2] == last_depth:
					return_list.append(tuplo)

			return return_list

		def find_mst_root(mst):
			for tuplo in mst:
				if tuplo[0] is None:
					return tuplo[1]

		def link_last(member, from_node, to_node, correspondence_list):

			if from_node is None:
				return

			new_from_node = find_correspondence(from_node, correspondence_list)

			all_from_nodes = list()
			for rule_idx in range(len(member.rule_list)):
				if member.rule_list[rule_idx].name == new_from_node:
					all_from_nodes.append(rule_idx)

			if len(all_from_nodes)>0:
				reached = False
				for rule_idx in all_from_nodes:
					for node in member.rule_list[rule_idx].node_list:
						if node.name == to_node:
							reached = True

				if reached is False:
					new_node = Node()
					new_node.name = to_node
					member.rule_list[random.choice(all_from_nodes)].node_list.append(new_node)

		def find_incoming_connections(member, mst_a_root, mst_b_root):
			for rule in member.rule_list:
				for node in rule.node_list:
					if node.name == mst_a_root:
						node.name = mst_b_root


		#restore incoming connections
		incoming_nodes = find_incoming_connections(new_member, find_mst_root(mst_a),find_mst_root(mst_b))

		#set based on correspondence_list
		for rule in new_member.rule_list:
			for node in rule.node_list:
				if find_correspondence(node.name, correspondence_list) in new_member.getDifferentRules():
						node.name = find_correspondence(node.name, correspondence_list)

		#ligacoes de saida
		last_level_list = last_level_nodes(mst_a, last_level(mst_a))

		for tuplo in last_level_list:
			link_last(new_member, tuplo[0], tuplo[1], correspondence_list)

		#startshape
		if new_member.startshape in subgraph_a:
			correspondence_startshape = find_correspondence(new_member.startshape, correspondence_list)
			if correspondence_startshape not in subgraph_b:
				new_member.startshape = find_mst_root(mst_b)
			else:
				new_member.startshape = correspondence_startshape

		#erase other connections
		new_member.setDifferentRules()

		for rule in new_member.rule_list:
			del_items = list()
			for node_idx in range(len(rule.node_list)):
				if rule.node_list[node_idx].name not in new_member.getDifferentRules()+['CIRCLE','TRIANGLE','SQUARE'] :
					del_items.append(node_idx)

			while(len(del_items)>0):
				del rule.node_list[del_items.pop()]

		

	# def stablish_correspondence(member, correspondence_list):
	# 	del_items = list()
	# 	for rule in member.rule_list:
	# 		for node_index in range(len(rule.node_list)):
	# 			if rule.node_list[node_index].name not in ['CIRCLE', 'SQUARE', 'TRIANGLE'] and rule.node_list[node_index].name not in member.getDifferentRules():
	# 				prev_node_name = rule.node_list[node_index].name
	# 				new_name = find_correspondence(rule.node_list[node_index].name, correspondence_list)

	# 				if new_name == prev_node_name:
	# 					del_items.append(node_index)
	# 				else:
	# 					rule.node_list[node_index].name = new_name

	# 		while(len(del_items)>0):
	# 			del rule.node_list[del_items.pop()]

	# 	member.setDifferentRules()

	# 	if member.startshape not in member.getDifferentRules():
	# 		member.startshape = find_correspondence(member.startshape, correspondence_list)


	new_a = copy_rules(subgraph_a, A, subgraph_b, B)
	new_b = copy_rules(subgraph_b, B, subgraph_a, A)

	new_a.setDifferentRules()
	new_b.setDifferentRules()

	stablish_correspondence(new_a, correspondence_list, mst_a, mst_b, subgraph_a, subgraph_b)
	stablish_correspondence(new_b, correspondence_list, mst_b, mst_a, subgraph_b, subgraph_a)

	new_a.setDifferentRules()
	new_b.setDifferentRules()

	return (new_a, new_b)




# ####### TEST ########
# def open_member(file_location):
# 	f_in = open(file_location,'r')
# 	fileContent = f_in.readlines()
# 	f_in.close()
	
# 	_str=""
# 	for line in fileContent:
# 		_str+=line.replace(' ','  ').replace('\n','  ').replace('\r','  ').replace('\t','  ').replace('{','{ ').replace('}',' }')

# 	pop_member=lexer.newMember(_str)
# 	pop_member.setDifferentRules()
# 	pop_member.classifyNodes()

# 	return pop_member

# A = open_member('A.cfdg')
# B = open_member('B.cfdg')

# crossover(A,B, 1)		