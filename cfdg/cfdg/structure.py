class PopMember:

	"""Class that represents an individual.
		An individual is formed by a set of rules that has a set of
		nodes that has a set of properties"""

	def __init__(self):
		self.startshape = None
		self.background = None
		self.rule_list = list()
		self.dif_rules = None
		self.fileName = None
		self.fitness = None
		self.fitness_dict = dict()
		self.statistics = None
		self.renderings = list()


	def addRendering(self,rendering_dir):
		new_render = Rendering(rendering_dir)
		self.renderings.append(new_render)

	def setStartshape(self,rule_name):
		self.startshape=rule_name

	def setBackground(self,node):
		self.background = node

	def addRule(self,new_rule):
		self.rule_list.append(new_rule)

	def getDifferentRules(self):
		return self.dif_rules

	def setDifferentRules(self):
		dif_rules = list()

		for rule in self.rule_list:
			if rule.name not in dif_rules:
				dif_rules.append(rule.name)

		self.dif_rules = dif_rules

	def classifyNodes(self):
		for rule in self.rule_list:
			for node in rule.node_list:
				if(node in self.dif_rules):
					node.final=False
				else:
					node.final=True


	def getDifferentSymbols(self):
		return_array = ['TRIANGLE','CIRCLE','SQUARE']

		for rule in self.rule_list:
			for node in rule.node_list:
				if node.name not in return_array:
					return_array.append(node.name)

		return return_array


	def getDifferentParameters(self,num_values):
		dif_param=list()

		for rule in self.rule_list:
			for node in rule.node_list:
				for parameter in node.parameters:
					if parameter.name not in dif_param and len(parameter.values)==num_values:
						dif_param.append(parameter.name)

		return dif_param

	def printMember(self):
		_str=""
		if self.startshape is not None:
			_str+= 'startshape '+self.startshape+'\n'

		if self.background is not None and len(self.background.parameters) > 0:

			_str+='background {'

			for parameter in self.background.parameters:
			    _str+=parameter.name+' '
			    for value in parameter.values:
			        _str+= "{:f}".format(value).rstrip("0")+' '
			_str+='}\n'

		for rule in self.rule_list:
		    _str+='rule '+rule.name+' '

		    if rule.probability is not None:
		        _str += "{:f}".format(rule.probability).rstrip("0")

		    _str+='{ '

		    if len(rule.node_list)>0:
		        _str+='\n'

		    for node in rule.node_list:
		        _str+='\t'+node.name +' { '
		        for parameter in node.parameters:
		            _str+=parameter.name+' '
		            for value in parameter.values:
		                _str+= "{:f}".format(value).rstrip("0")+' '
		        _str+='}\n'

		    _str+='}\n'

		return _str

class Rendering:
	def __init__(self, directory):
		self.dir = directory
		self.fitness = None
		self.fitness_dict = dict()


class Rule:
	def __init__(self):
		self.name = None
		self.probability = None
		self.node_list = []

	def setName(self,new_name):
		self.name=new_name

	def setProbability(self,new_prob):
		self.probability=new_prob

	def addNode(self,new_node):
		self.node_list.append(new_node)

class Node:
	def __init__(self):
		self.parameters = []
		self.name = None
		self.final = None

	def setName(self,new_name):
		self.name = new_name

	def addParameter(self,new_prop):
		self.parameters.append(new_prop)

class Parameter:
	def __init__(self):
		self.name = None
		self.values = []

	def setName(self,new_name):
		self.name=new_name

	def addValue(self,new_value):
		self.values.append(new_value)