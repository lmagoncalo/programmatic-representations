from numpy import mean, std
from count_useless import count_useless_rules
from count_productive import count_productive_total


def generate_final_gen(pop):

	for member in pop:
		member.statistics = Statistics()
		[member.statistics.num_rules, member.statistics.dif_rules, member.statistics.total_reachable, 
		member.statistics.total_unreachable, member.statistics.reachable, member.statistics.unreachable,
		member.statistics.per_total_reachable, member.statistics.per_total_unreachable,
		member.statistics.per_reachable, member.statistics.per_unreachable]=count_useless_rules(member)
		[member.statistics.productive, member.statistics.unproductive, member.statistics.per_productive,
		member.statistics.per_unproductive] = count_productive_total(member)


	num_rules = []
	dif_rules = []
	total_reachable = []
	total_unreachable = []
	reachable = []
	unreachable = []
	per_total_unreachable = []
	per_total_reachable = []
	per_reachable = []
	per_unreachable = []

	productive = []
	unproductive = []
	per_productive = []
	per_unproductive = []

	fitness_guide = []
	fitness_dict = {}
	
	for other_fit in member.fitness_dict.keys():
		fitness_dict[other_fit]=list()

	for member in pop:
		num_rules.append(member.statistics.num_rules)
		dif_rules.append(member.statistics.dif_rules)
		total_reachable.append(member.statistics.total_reachable)
		total_unreachable.append(member.statistics.total_unreachable)
		reachable.append(member.statistics.reachable)
		unreachable.append(member.statistics.unreachable)

		per_total_reachable.append(member.statistics.per_total_reachable)
		per_total_unreachable.append(member.statistics.per_total_unreachable)
		per_reachable.append(member.statistics.per_reachable)
		per_unreachable.append(member.statistics.per_unreachable)

		productive.append(member.statistics.productive)
		unproductive.append(member.statistics.unproductive)
		per_productive.append(member.statistics.per_productive)
		per_unproductive.append(member.statistics.per_unproductive)

		fitness_guide.append(member.fitness)

		for other_fit in member.fitness_dict.keys():
			fitness_dict[other_fit] += [member.fitness_dict[other_fit]]


	other_fit_stats = list()
	print(fitness_dict)
	for other_fit in fitness_dict.keys():
		other_fit_stats += get_global_local(fitness_dict[other_fit], pop)[0]

	num_rules_stats = get_global_local(num_rules, pop)

	return [num_rules_stats[1]]+num_rules_stats[0]+get_global_local(dif_rules, pop)[0]+get_global_local(total_reachable, pop)[0]+get_global_local(total_unreachable, pop)[0]+get_global_local(reachable, pop)[0]+get_global_local(total_unreachable, pop)[0]+get_global_local(per_total_reachable, pop)[0]+get_global_local(per_total_unreachable, pop)[0]+get_global_local(per_reachable, pop)[0]+get_global_local(per_unreachable, pop)[0]+get_global_local(productive, pop)[0]+get_global_local(unproductive, pop)[0]+get_global_local(per_productive, pop)[0]+get_global_local(per_unproductive, pop)[0]+get_global_local(fitness_guide, pop)[0]+other_fit_stats        



def get_global_local(array, pop):
	_max = max(array)
	_min_global = min(array)
	_mean_global = mean(array)
	_std_global = std(array)

	array_local = list()
	for index in range(len(pop)):
		if(pop[index].fitness > 0):
			array_local.append(array[index])

	_min_local = min(array_local)
	_mean_local = mean(array_local)
	_std_local = std(array_local)

	_non_rendered = len(array)-len(array_local)

	return ([_max, _min_global, _min_local, _mean_global, _mean_local, _std_global, _std_local], _non_rendered)


class Statistics:

	def __init__(self):
		self.num_rules = None
		self.dif_rules = None
		self.total_reachable = None
		self.total_unreachable = None
		self.reachable = None
		self.unreachable = None
		self.per_total_reachable = None
		self.per_total_unreachable = None
		self.per_reachable = None
		self.per_unreachable = None
		self.productive = None
		self.unproductive = None
		self.per_productive = None
		self.per_unproductive = None


	def as_array(self):
		return [self.num_rules, self.dif_rules, self.total_reachable, self.total_unreachable, self.reachable, self.unreachable,
		self.per_total_reachable, self.per_total_unreachable, self.per_reachable, self.per_unreachable, self.productive,
		self.unproductive, self.per_productive, self.per_unproductive]
