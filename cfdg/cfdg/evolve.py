import copy
import glob
import logging
import operator
import random
import sys
import traceback
from threading import Thread

import clip
import numpy
import torch

import fitness
import initial_pop_random
import lexer
from laion_aesthetics import init_laion
from configure import Config
from crossover import crossover
from csv_management import write_content
from fitness import *
from get_n_best import get_best
from mutation import check_member_validity
from mutation import mutation
from statistical import generate_final_gen


# ACTIVE_MODELS = None
# TARGET_CLASS = "birdhouse"
# NETWORKS = "vgg16"

class EvolutionaryEngine:

    def threaded_function(self, threadNumber, runs):
        try:
            for run in runs:
                print('Run ' + str(run))
                random.seed(self.config_file.seeds[self.seed])

                os.makedirs(self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed])
                os.makedirs(self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/initial_pop/')
                os.makedirs(self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/fitness/')

                print('[' + str(run) + '] Initial Pop')
                self.initial_pop = self.open_initial_pop(run)

                new_population = copy.deepcopy(self.initial_pop)
                for generation in range(self.config_file.num_generations):
                    print('[' + str(run) + '] Generation ' + str(generation))
                    os.makedirs(self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/pop' + str(generation))

                    current_population = copy.deepcopy(new_population)
                    new_population = []

                    selection_output = self.tournament_selection(current_population, self.config_file.tournament_size)

                    for pop_element in range(0, len(selection_output), 2):

                        first_debug = True

                        # parents selection
                        parents = random.sample(selection_output, 2)

                        A = copy.deepcopy(parents[0])
                        B = copy.deepcopy(parents[1])

                        if first_debug is True and (
                                check_member_validity(A) is False or check_member_validity(B) is False):
                            logging.debug('Error checking member validity at the begining')
                            first_debug = False

                        self.swapRuleNames(A, '_A')
                        self.swapRuleNames(B, '_B')
                        A.setDifferentRules()
                        B.setDifferentRules()

                        if first_debug is True and (
                                check_member_validity(A) is False or check_member_validity(B) is False):
                            logging.debug('Error checking member validity after swapping rule names')
                            first_debug = False

                        name_A = A.fileName
                        name_B = B.fileName

                        # crossover
                        crossover_tuple = crossover(A, B, self.config_file.crossover_probability, random.getstate())

                        new_A = copy.deepcopy(crossover_tuple[0])
                        new_B = copy.deepcopy(crossover_tuple[1])

                        random.setstate(crossover_tuple[2])

                        new_A.setDifferentRules()
                        new_B.setDifferentRules()

                        if first_debug is True and (
                                check_member_validity(new_A) is False or check_member_validity(new_B) is False):
                            logging.debug('Error checking member validity after crossover')
                            first_debug = False

                        # mutation
                        random.setstate(mutation(new_A, self.config_file.mutation_startshape,
                                                 self.config_file.mutation_background_rename,
                                                 self.config_file.mutation_background_value,
                                                 self.config_file.mutation_background_mu,
                                                 self.config_file.mutation_background_std,
                                                 self.config_file.mutation_parameter_rename,
                                                 self.config_file.mutation_parameter_remove,
                                                 self.config_file.mutation_parameter_value,
                                                 self.config_file.mutation_parameter_mu,
                                                 self.config_file.mutation_parameter_std,
                                                 self.config_file.mutation_rule_duplicate,
                                                 self.config_file.mutation_rule_remove,
                                                 self.config_file.mutation_rule_copyRename,
                                                 self.config_file.mutation_symbol_remove,
                                                 self.config_file.mutation_symbol_replace,
                                                 self.config_file.mutation_symbol_add, random.getstate()))

                        random.setstate(mutation(new_B, self.config_file.mutation_startshape,
                                                 self.config_file.mutation_background_rename,
                                                 self.config_file.mutation_background_value,
                                                 self.config_file.mutation_background_mu,
                                                 self.config_file.mutation_background_std,
                                                 self.config_file.mutation_parameter_rename,
                                                 self.config_file.mutation_parameter_remove,
                                                 self.config_file.mutation_parameter_value,
                                                 self.config_file.mutation_parameter_mu,
                                                 self.config_file.mutation_parameter_std,
                                                 self.config_file.mutation_rule_duplicate,
                                                 self.config_file.mutation_rule_remove,
                                                 self.config_file.mutation_rule_copyRename,
                                                 self.config_file.mutation_symbol_remove,
                                                 self.config_file.mutation_symbol_replace,
                                                 self.config_file.mutation_symbol_add, random.getstate()))

                        if first_debug is True and (
                                check_member_validity(new_A) is False or check_member_validity(new_B) is False):
                            logging.debug('Error checking member validity after mutation')
                            first_debug = False

                        # write cfdgs to .cfdg file
                        os.makedirs(
                            self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/pop' + str(generation) + '/ind' + str(pop_element))
                        self.write_file(
                            self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/pop' + str(generation) + '/ind' + str(pop_element) + '/' + str(
                                run) + '_' + str(generation) + '_' + str(pop_element) + '.cfdg', new_A.printMember())
                        os.makedirs(
                            self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/pop' + str(generation) + '/ind' + str(pop_element + 1))
                        self.write_file(
                            self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/pop' + str(generation) + '/ind' + str(pop_element + 1) + '/' + str(
                                run) + '_' + str(generation) + '_' + str(pop_element + 1) + '.cfdg',
                            new_B.printMember())

                        new_A.fileName = self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/pop' + str(generation) + '/ind' + str(
                            pop_element) + '/' + str(run) + '_' + str(generation) + '_' + str(pop_element) + '.cfdg'
                        new_B.fileName = self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/pop' + str(generation) + '/ind' + str(
                            pop_element + 1) + '/' + str(run) + '_' + str(generation) + '_' + str(
                            pop_element + 1) + '.cfdg'

                        # cfdg rendering to .png
                        fitness.renderGrammar(new_A, new_A.fileName, new_A.fileName.split('.cfdg')[0] + '.png',
                                              self.config_file.contextfree_seed,
                                              rendering_time=self.config_file.rendering_time,
                                              max_generations=self.config_file.max_renderer)
                        fitness.renderGrammar(new_B, new_B.fileName, new_B.fileName.split('.cfdg')[0] + '.png',
                                              self.config_file.contextfree_seed,
                                              rendering_time=self.config_file.rendering_time,
                                              max_generations=self.config_file.max_renderer)

                        # add childs to current population
                        new_population.append(new_A)
                        new_population.append(new_B)

                    fitness.classifyFitness(new_population, self.config_file.fitness_function, True)

                    new_population = self.elite_selection(current_population, new_population,
                                                          self.config_file.elite_size)

                    fitness.classifyFitness(new_population[:self.config_file.elite_size],
                                            self.config_file.fitness_function, True)

                    # other fitnesses stats
                    fitness.classifyFitness(new_population, self.config_file.other_fitnesses, False)

                    # STATISTICS TO FILE!
                    # header
                    to_append_write = ''
                    if not os.path.isfile(
                            self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/fitness/run_statistics.csv'):
                        to_append_write = 'Generation,Non Renderable CFDGs, Max Num. Rules, [Global] Min Num. Rules,[Local] Min Num. Rules,[Global] AVG Num. Rules,[Local] AVG Num. Rules,[Global] STD Num. Rules,[Local] STD Num. Rules,Max Dif. Rules, [Global] Min Dif. Rules,[Local] Min Dif. Rules,[Global] AVG Dif. Rules,[Local] AVG Dif. Rules,[Global] STD Dif. Rules,[Local] STD Dif. Rules,Max Total Reachable Rules, [Global] Min Total Reachable Rules,[Local] Min Total Reachable Rules,[Global] AVG Total Reachable Rules,[Local] AVG Total Reachable Rules,[Global] STD Total Reachable Rules,[Local] STD Total Reachable Rules,Max Total Unreachable Rules, [Global] Min Total Unreachable Rules,[Local] Min Total Unreachable Rules,[Global] AVG Total Unreachable Rules,[Local] AVG Total Unreachable Rules,[Global] STD Total Unreachable Rules,[Local] STD Total Unreachable Rules,Max Reachable Rules, [Global] Min Reachable Rules,[Local] Min Reachable Rules,[Global] AVG Reachable Rules,[Local] AVG Reachable Rules,[Global] STD Reachable Rules,[Local] STD Reachable Rules,Max Unreachable Rules, [Global] Min Unreachable Rules,[Local] Min Unreachable Rules,[Global] AVG Unreachable Rules,[Local] AVG Unreachable Rules,[Global] STD Unreachable Rules,[Local] STD Unreachable Rules,Max % Total Reachable, [Global] Min % Total Reachable,[Local] Min % Total Reachable,[Global] AVG % Total Reachable,[Local] AVG % Total Reachable,[Global] STD % Total Reachable,[Local] STD % Total Reachable,Max % Total Unreachable, [Global] Min % Total Unreachable,[Local] Min % Total Unreachable,[Global] AVG % Total Unreachable,[Local] AVG % Total Unreachable,[Global] STD % Total Unreachable,[Local] STD % Total Unreachable,Max % Reachable, [Global] Min % Reachable,[Local] Min % Reachable,[Global] AVG % Reachable,[Local] AVG % Reachable,[Global] STD % Reachable,[Local] STD % Reachable,Max % Unreachable, [Global] Min % Unreachable,[Local] Min % Unreachable,[Global] AVG % Unreachable,[Local] AVG % Unreachable,[Global] STD % Unreachable,[Local] STD % Unreachable,Max Productive,[Global] Min Productive,[Local] Min Productive,[Global] AVG Productive,[Local] AVG Productive,[Global] STD Productive,[Local] STD Productive,Max Unproductive,[Global] Min Unproductive,[Local] Min Unproductive,[Global] AVG Unproductive,[Local] AVG Unproductive,[Global] STD Unproductive,[Local] STD Unproductive,Max % Productive,[Global] Min % Productive,[Local] Min % Productive,[Global] AVG % Productive,[Local] AVG % Productive,[Global] STD % Productive,[Local] STD % Productive,Max % Unproductive,[Global] Min % Unproductive,[Local] Min % Unproductive,[Global] AVG % Unproductive,[Local] AVG % Unproductive,[Global] STD % Unproductive,[Local] STD % Unproductive'
                        to_append_write += ',Max ' + '_'.join(
                            self.config_file.fitness_function) + ',[Global] Min ' + '_'.join(
                            self.config_file.fitness_function) + ',[Local] Min ' + '_'.join(
                            self.config_file.fitness_function) + ',[Global] AVG ' + '_'.join(
                            self.config_file.fitness_function) + ',[Local] AVG ' + '_'.join(
                            self.config_file.fitness_function) + ',[Global] STD ' + '_'.join(
                            self.config_file.fitness_function) + ',[Local] STD ' + '_'.join(
                            self.config_file.fitness_function)
                        for other_fit in self.config_file.other_fitnesses:
                            to_append_write += ',Max ' + other_fit + ',[Global] Min ' + other_fit + ',[Local] Min ' + other_fit + ',[Global] AVG ' + other_fit + ',[Local] AVG ' + other_fit + ',[Global] STD ' + other_fit + ',[Local] STD ' + other_fit
                        to_append_write += '\n'

                    output = [generation] + generate_final_gen(new_population)
                    f_out = open(self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/fitness/run_statistics.csv', 'a')

                    f_out.write(to_append_write)

                    for indx in range(len(output)):
                        if indx > 0:
                            f_out.write(',')

                        f_out.write(str(output[indx]))

                    f_out.write('\n')
                    f_out.close()

                    data_fitness_csv = [
                        ["Filename", "# Rules", "Dif Rules", "Total Reachable Rules", "Total Unreachable Rules",
                         "Reachable Rules", "Unreachable Rules", "%Total Reachable", "%Total Unreachable",
                         "% Reachable", "% Unreachable", "Productive Rules", "Unproductive Rules", "% Productive",
                         "% Unproductive",
                         '_'.join(self.config_file.fitness_function)] + self.config_file.other_fitnesses]
                    for member in new_population:
                        data_fitness_csv.append([member.fileName.split('/').pop()])
                        data_fitness_csv[len(data_fitness_csv) - 1].extend(member.statistics.as_array())
                        data_fitness_csv[len(data_fitness_csv) - 1].extend([member.fitness])

                        other_fitnesses_list = list()
                        for fitness_name in self.config_file.other_fitnesses:
                            other_fitnesses_list.append(member.fitness_dict[fitness_name])

                        data_fitness_csv[len(data_fitness_csv) - 1].extend(other_fitnesses_list)

                        for render in member.renderings:
                            if render.fitness == 0:
                                logging.debug('Error: image not rendered: ' + render.dir)
                            else:
                                prev_dir = render.dir
                                render.dir = render.dir.replace('.png', '') + '_#' + str(int(render.fitness)) + '.png'
                                os.rename(prev_dir, render.dir)

                        os.rename(member.fileName,
                                  member.fileName.split(".cfdg")[0] + '_#' + str(member.fitness) + '.cfdg')
                        member.fileName = member.fileName.split(".cfdg")[0] + '_#' + str(member.fitness) + '.cfdg'

                    write_content(self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/fitness/pop' + str(generation) + '.csv', data_fitness_csv, assure_new=True,
                                  multiple=True)

                    if self.config_file.fitness_function[0] == 'bell':
                        new_population = self.sort_bell(new_population)

                    else:
                        new_population.sort(key=operator.attrgetter('fitness'), reverse=True)
        except Exception as err:
            logging.debug('Thread ' + str(threadNumber) + ' ' + str(traceback.format_exc()))

    def __init__(self):
        self.logging = "logger.log"
        logging.basicConfig(filename=self.logging, level=logging.DEBUG)

        self.config_file = Config('config.cfg')
        self.config_file.readCfgFile()
        num_threads = 1  # Change this?
        self.best_number = 10
        self.prompt = sys.argv[3]
        self.seed = int(sys.argv[1])
        self.config_file.num_generations = int(sys.argv[2])

        print("Number of generations: ", self.config_file.num_generations)

        print(("Setting seed: ", self.seed))
        random.seed(self.seed)
        np.random.seed(self.seed)
        # tf.random.set_seed(self.seed)

        self.device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        aesthetic_model, vit_model, preprocess = init_laion(self.device)

        text_inputs = clip.tokenize(self.prompt).to(self.device)
        with torch.no_grad():
            text_features = vit_model.encode_text(text_inputs)

        def calculate_fitness(pil_image):
            image = preprocess(pil_image).unsqueeze(0).to(self.device)

            # extract the image features from the clip vit encoding
            with torch.no_grad():
                image_features = vit_model.encode_image(image)
            # im_emb_arr = normalizer(image_features.cpu().detach().numpy())
            # get aesthetic prediction from the laion model
            # prediction = aesthetic_model(torch.from_numpy(im_emb_arr).to(device).type(torch.float))
            # aesthetic_eval_laion = prediction.item()

            # calculate the cosine similarity between the text features
            # of the prompt and the image features of the current individual
            similarity = torch.cosine_similarity(text_features, image_features, dim=-1).mean()

            # fitness assignment!
            # 1 - just similarity between image features and text features
            ind_fitness = similarity.item()

            return ind_fitness

        fitness.CLIP_FITNESS = calculate_fitness

        self.config_file.output_directory = self.config_file.output_directory + '/' + '_'.join(self.config_file.fitness_function) + '_' + self.prompt.replace(' ', '_')

        os.makedirs(self.config_file.output_directory, exist_ok=True)

        self.num_threads = num_threads

        if self.config_file.num_runs < self.num_threads:
            self.num_threads = self.config_file.num_runs

        num_runs_per_thread = int(self.config_file.num_runs / self.num_threads)
        self.threads = []
        for thread_index in range(self.num_threads):
            t = Thread(target=self.threaded_function, args=(
            thread_index, range(thread_index * num_runs_per_thread, (thread_index + 1) * num_runs_per_thread)))
            self.threads.append(t)
            self.threads[thread_index].start()

        for threads_index in range(self.num_threads):
            self.threads[threads_index].join()

        self.generateFinalStats()

        # get N (=best_number) best elements
        runs_list = list()
        for run in range(self.config_file.num_runs):
            runs_list.append(self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed])

        get_best(self.best_number, runs_list, self.config_file.output_directory + '/best_individuals')

    def generateFinalStats(self):

        def work_in_range(idx_min, idx_max, files_list):
            _max = [[] for _ in range(self.config_file.num_generations)]
            global_min = [[] for _ in range(self.config_file.num_generations)]
            local_min = [[] for _ in range(self.config_file.num_generations)]
            global_mean = [[] for _ in range(self.config_file.num_generations)]
            local_mean = [[] for _ in range(self.config_file.num_generations)]
            global_std = [[] for _ in range(self.config_file.num_generations)]
            local_std = [[] for _ in range(self.config_file.num_generations)]

            for file_content in files_list:
                file_content = file_content[1:]
                for generation in range(self.config_file.num_generations):
                    for col in range(idx_min, idx_max):

                        idx = col - idx_min

                        if idx == 0:
                            _max[generation].append(float(file_content[generation][col]))

                        elif idx == 1:
                            global_min[generation].append(float(file_content[generation][col]))

                        elif idx == 2:
                            local_min[generation].append(float(file_content[generation][col]))

                        elif idx == 3:
                            global_mean[generation].append(float(file_content[generation][col]))

                        elif idx == 4:
                            local_mean[generation].append(float(file_content[generation][col]))

                        elif idx == 5:
                            global_std[generation].append(float(file_content[generation][col]))

                        elif idx == 6:
                            local_std[generation].append(float(file_content[generation][col]))

            output = list()

            for gen in range(self.config_file.num_generations):
                output.append([max(_max[gen]), min(global_min[gen]), min(local_min[gen]), numpy.mean(global_mean[gen]),
                               numpy.mean(local_mean[gen]), numpy.mean(global_std[gen]), numpy.mean(local_std[gen])])

            return output

        def get_non_renderable(col, files_list):

            non_renderable = [[] for x in range(self.config_file.num_generations)]

            for file_content in files_list:
                file_content = file_content[1:]
                for generation in range(self.config_file.num_generations):
                    non_renderable[generation].append(float(file_content[generation][col]))

            output = list()

            for gen in range(self.config_file.num_generations):
                output.append([max(non_renderable[gen]), min(non_renderable[gen]), numpy.mean(non_renderable[gen]),
                               numpy.std(non_renderable[gen])])

            return output

        def to_string(array, last=False):
            output = ''

            if not last:
                for elem in array:
                    output += str(elem) + ','

            else:
                for idx in range(len(array)):
                    if (idx < len(array) - 1):
                        output += str(array[idx]) + ','
                    else:
                        output += str(array[idx]) + '\n'
            return output

        files_list = list()
        for run in range(self.config_file.num_runs):
            folder = self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/fitness/'

            f_content_split = list()

            f = open(folder + 'run_statistics.csv', 'r')
            file_content = f.readlines()

            for line in file_content:
                line_content = line.replace('\r', '').replace('\n', '').split(',')
                f_content_split.append(line_content)
            f.close()

            files_list.append(f_content_split)

        non_renderable = get_non_renderable(1, files_list)
        num_rules = work_in_range(2, 9, files_list)
        dif_rules = work_in_range(9, 16, files_list)
        total_reachable = work_in_range(16, 23, files_list)
        total_unreachable = work_in_range(23, 30, files_list)
        reachable = work_in_range(30, 37, files_list)
        unreachable = work_in_range(37, 44, files_list)
        per_total_reachable = work_in_range(44, 51, files_list)
        per_total_unreachable = work_in_range(51, 58, files_list)
        per_reachable = work_in_range(58, 65, files_list)
        per_unreachable = work_in_range(65, 72, files_list)

        productive = work_in_range(72, 79, files_list)
        unproductive = work_in_range(79, 86, files_list)
        per_productive = work_in_range(86, 93, files_list)
        per_unproductive = work_in_range(93, 100, files_list)

        guide_fitness = work_in_range(100, 107, files_list)
        other_fitnesses = list()

        for x in range(len(self.config_file.other_fitnesses)):
            other_fitnesses.append(work_in_range(107 + x * 7, 107 + (x + 1) * 7, files_list))

        f_out = open(self.config_file.output_directory + '/global.csv', 'w')

        f_out.write(
            'Generation,Max Non-Renderable,Min Non-Renderable,AVG Non-Renderable,STD Non-Renderable,Max Num. Rules, [Global] Min Num. Rules,[Local] Min Num. Rules,[Global] AVG Num. Rules,[Local] AVG Num. Rules,[Global] STD Num. Rules,[Local] STD Num. Rules,Max Dif. Rules, [Global] Min Dif. Rules,[Local] Min Dif. Rules,[Global] AVG Dif. Rules,[Local] AVG Dif. Rules,[Global] STD Dif. Rules,[Local] STD Dif. Rules,Max Total Reachable Rules, [Global] Min Total Reachable Rules,[Local] Min Total Reachable Rules,[Global] AVG Total Reachable Rules,[Local] AVG Total Reachable Rules,[Global] STD Total Reachable Rules,[Local] STD Total Reachable Rules,Max Total Unreachable Rules, [Global] Min Total Unreachable Rules,[Local] Min Total Unreachable Rules,[Global] AVG Total Unreachable Rules,[Local] AVG Total Unreachable Rules,[Global] STD Total Unreachable Rules,[Local] STD Total Unreachable Rules,Max Reachable Rules, [Global] Min Reachable Rules,[Local] Min Reachable Rules,[Global] AVG Reachable Rules,[Local] AVG Reachable Rules,[Global] STD Reachable Rules,[Local] STD Reachable Rules,Max Unreachable Rules, [Global] Min Unreachable Rules,[Local] Min Unreachable Rules,[Global] AVG Unreachable Rules,[Local] AVG Unreachable Rules,[Global] STD Unreachable Rules,[Local] STD Unreachable Rules,Max % Total Reachable, [Global] Min % Total Reachable,[Local] Min % Total Reachable,[Global] AVG % Total Reachable,[Local] AVG % Total Reachable,[Global] STD % Total Reachable,[Local] STD % Total Reachable,Max % Total Unreachable, [Global] Min % Total Unreachable,[Local] Min % Total Unreachable,[Global] AVG % Total Unreachable,[Local] AVG % Total Unreachable,[Global] STD % Total Unreachable,[Local] STD % Total Unreachable,Max % Reachable, [Global] Min % Reachable,[Local] Min % Reachable,[Global] AVG % Reachable,[Local] AVG % Reachable,[Global] STD % Reachable,[Local] STD % Reachable,Max % Unreachable, [Global] Min % Unreachable,[Local] Min % Unreachable,[Global] AVG % Unreachable,[Local] AVG % Unreachable,[Global] STD % Unreachable,[Local] STD % Unreachable,Max Productive,[Global] Min Productive,[Local] Min Productive,[Global] AVG Productive,[Local] AVG Productive,[Global] STD Productive,[Local] STD Productive,Max Unproductive,[Global] Min Unproductive,[Local] Min Unproductive,[Global] AVG Unproductive,[Local] AVG Unproductive,[Global] STD Unproductive,[Local] STD Unproductive,Max % Productive,[Global] Min % Productive,[Local] Min % Productive,[Global] AVG % Productive,[Local] AVG % Productive,[Global] STD % Productive,[Local] STD % Productive,Max % Unproductive,[Global] Min % Unproductive,[Local] Min % Unproductive,[Global] AVG % Unproductive,[Local] AVG % Unproductive,[Global] STD % Unproductive,[Local] STD % Unproductive')
        f_out.write(',Max ' + '_'.join(self.config_file.fitness_function) + ',[Global] Min ' + '_'.join(
            self.config_file.fitness_function) + ',[Local] Min ' + '_'.join(
            self.config_file.fitness_function) + ',[Global] AVG ' + '_'.join(
            self.config_file.fitness_function) + ',[Local] AVG ' + '_'.join(
            self.config_file.fitness_function) + ',[Global] STD ' + '_'.join(
            self.config_file.fitness_function) + ',[Local] STD ' + '_'.join(self.config_file.fitness_function))
        for other_fit in self.config_file.other_fitnesses:
            f_out.write(
                ',Max ' + other_fit + ',[Global] Min ' + other_fit + ',[Local] Min ' + other_fit + ',[Global] AVG ' + other_fit + ',[Local] AVG ' + other_fit + ',[Global] STD ' + other_fit + ',[Local] STD ' + other_fit)

        f_out.write('\n')

        for generation in range(self.config_file.num_generations):
            f_out.write(str(generation) + ',' + to_string(non_renderable[generation]) + to_string(
                num_rules[generation]) + to_string(dif_rules[generation]) + to_string(
                total_reachable[generation]) + to_string(total_unreachable[generation]) + to_string(
                reachable[generation]) + to_string(unreachable[generation]) + to_string(
                per_total_reachable[generation]) + to_string(per_total_unreachable[generation]) + to_string(
                per_reachable[generation]) + to_string(per_unreachable[generation]) + to_string(
                productive[generation]) + to_string(unproductive[generation]) + to_string(
                per_productive[generation]) + to_string(per_unproductive[generation]) + to_string(
                guide_fitness[generation]))
            for x in range(len(other_fitnesses)):
                if x < len(other_fitnesses) - 1:
                    f_out.write(to_string(other_fitnesses[x][generation]))
                else:
                    f_out.write(to_string(other_fitnesses[x][generation], True))
        f_out.close()

    def sort_bell(self, population_array):

        population = copy.deepcopy(population_array)
        negative_fitnesses = list()
        positive_fitnesses = list()
        zero_fitnesses = list()

        for member in population:
            if member.fitness > 0:
                positive_fitnesses.append(member)
            elif member.fitness < 0:
                negative_fitnesses.append(member)
            else:
                zero_fitnesses.append(member)

        negative_fitnesses.sort(key=operator.attrgetter('fitness'), reverse=True)
        positive_fitnesses.sort(key=operator.attrgetter('fitness'), reverse=True)
        zero_fitnesses.sort(key=operator.attrgetter('fitness'), reverse=True)

        return negative_fitnesses + positive_fitnesses + zero_fitnesses

    def swapRuleNames(self, member, string):

        rules = []

        for rule in member.rule_list:
            if rule.name not in rules:
                rules.append(rule.name)

        if member.startshape in rules:
            member.startshape = member.startshape + string

        for rule in member.rule_list:
            if (rule.name in rules):
                rule.name = rule.name + string
                for node in rule.node_list:
                    if node.name in rules:
                        node.name = node.name + string

    def write_file(self, output_dir, content):
        f = open(output_dir, 'w')
        f.write(content)
        f.close()

    def open_initial_pop_member(self, file_location):
        f_in = open(file_location, 'r')
        fileContent = f_in.readlines()
        f_in.close()

        _str = ""
        for line in fileContent:
            _str += line.replace(' ', '  ').replace('\n', '  ').replace('\r', '  ').replace('\t', '  ').replace('{',
                                                                                                                '{ ').replace(
                '}', ' }')

        pop_member = lexer.newMember(_str)
        pop_member.setDifferentRules()
        pop_member.classifyNodes()

        return pop_member

    def open_initial_pop(self, run):
        if self.config_file.initial_pop_directory is None:
            initial_pop = []
            random_pop = initial_pop_random.generateInitialPopulation(
                self.config_file.output_directory + '/run_' + str(self.seed) + '_' + self.config_file.seeds[self.seed] + '/initial_pop', self.config_file.fitness_function, self.config_file.pop_size, run,
                self.config_file.contextfree_seed, self.config_file.seeds[self.seed], self.config_file.max_renderer,
                self.config_file.rendering_time)
            return random_pop

        elif type(self.config_file.initial_pop_directory) is str:
            initial_pop = []
            array_files = []

            array_files = glob.glob(self.config_file.initial_pop_directory + '/*.cfdg')

            for _file in array_files:
                pop_member = self.open_initial_pop_member(_file)
                pop_member.fileName = _file
                initial_pop.append(pop_member)
                fitness.renderGrammar(pop_member, pop_member.fileName, pop_member.fileName.split('.cfdg')[0] + '.png',
                                      self.config_file.contextfree_seed, rendering_time=self.config_file.rendering_time,
                                      max_generations=self.config_file.max_renderer)

            classifyFitness(initial_pop, self.config_file.fitness_function, True)

            return initial_pop

    def tournament_selection(self, population, tournament_size):

        size = len(population)
        output = []
        population = copy.deepcopy(population)

        for it in range(size):
            sample = random.sample(population, tournament_size)

            if self.config_file.fitness_function[0] == 'bell':
                sample = self.sort_bell(sample)
            else:
                sample.sort(key=operator.attrgetter('fitness'), reverse=True)

            output.append(sample[0])

        return output

    def elite_selection(self, old_pop, new_pop, elite_size):

        if self.config_file.fitness_function[0] == 'bell':
            new_pop = self.sort_bell(new_pop)
            old_pop = self.sort_bell(old_pop)
        else:
            new_pop.sort(key=operator.attrgetter('fitness'), reverse=True)
            old_pop.sort(key=operator.attrgetter('fitness'), reverse=True)
        temp_pop = copy.deepcopy(old_pop[:elite_size]) + copy.deepcopy(new_pop[:len(new_pop) - elite_size])

        names_rename = [names.fileName for names in new_pop[len(new_pop) - elite_size:]]

        for current_member_elite in temp_pop[:elite_size]:
            new_fileName = names_rename.pop()
            self.write_file(new_fileName, current_member_elite.printMember())
            current_member_elite.fileName = new_fileName
            fitness.renderGrammar(current_member_elite, current_member_elite.fileName,
                                  current_member_elite.fileName.split('.cfdg')[0] + '.png',
                                  self.config_file.contextfree_seed, rendering_time=self.config_file.rendering_time,
                                  max_generations=self.config_file.max_renderer)

        return temp_pop


if __name__ == "__main__":
    EvolutionaryEngine()
