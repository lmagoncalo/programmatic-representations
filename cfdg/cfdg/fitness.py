import os

import contrasting_colours
from rendering import Command
from run_jars import run_frac_lac, run_aesthetic
from random import choice
# from blackwhite import calcParameters
from PIL import Image
from string import ascii_uppercase, ascii_lowercase
import numpy as np

ACTIVE_MODELS = None
IMAGENET_INDEXES = None
CLIP_FITNESS = None


def renderGrammar(member, origin, destination, contextfree_seed=None, rendering_time=None, max_generations=1000000,
                  width=256, height=256):
    def generateRandomSeed(length=5):
        chars = ascii_uppercase + ascii_lowercase
        random_generated = ''.join(choice(chars) for x in range(length))
        return random_generated

    member.renderings = list()

    if contextfree_seed is not None:
        if type(contextfree_seed) is str:
            fitness = ' -v ' + contextfree_seed
            destination = destination.split('.png')[0] + '_' + contextfree_seed + '.png'
            # print destination
            # print './cfdg '+fitness+' -w '+str(width)+' -h '+str(height)+' -N '+max_generations+' -o '+destination + ' ' + origin
            Command('./cfdg ' + fitness + ' -w ' + str(width) + ' -h ' + str(
                height) + ' -N ' + max_generations + ' -o ' + destination + ' ' + origin, rendering_time)
            member.addRendering(destination)
        elif type(contextfree_seed) is list:
            prev_destination = destination
            split_destination = prev_destination.replace('.png', '').split('/')[-1].split('_')
            for seed in contextfree_seed:
                fitness = ' -v ' + seed + ' '

                destination = '/'.join(prev_destination.split('/')[:-1])
                destination += '/' + split_destination[0] + '_' + split_destination[1] + '_' + split_destination[
                    2] + '_' + seed + '.png'

                Command('./cfdg ' + origin + fitness + ' -w ' + str(width) + ' -h ' + str(
                    height) + ' -N ' + max_generations + ' -o ' + destination, rendering_time)
                member.addRendering(destination)
        elif type(contextfree_seed) is int:
            prev_destination = destination
            for r in range(contextfree_seed):
                random_seed = generateRandomSeed()

                fitness = ' -v ' + random_seed + ' '

                destination = prev_destination.split('.png')[0] + '_' + random_seed + '.png'
                Command('./cfdg ' + origin + fitness + ' -w ' + str(width) + ' -h ' + str(
                    height) + ' -N ' + max_generations + ' -o ' + destination, rendering_time)
                member.addRendering(destination)


def generate_jpeg(file_dir):
    try:
        child_image = Image.open(file_dir)
        child_image.save(file_dir.split('.png')[0] + '.jpg', "JPEG", quality=100)
        jpeg_size = os.path.getsize(file_dir.split('.png')[0] + '.jpg')

    except IOError:
        jpeg_size = 0

    return jpeg_size


def fileSize(fileName):
    try:
        st = os.stat(fileName)

        return st.st_size
    except Exception as err:
        print(err, fileName)
        return 0


def size_jpg(files_list):
    fitness_list = list()

    for ficheiro in files_list:
        fitness_list.append(generate_jpeg(ficheiro))

    return fitness_list


def size_png(files_list):
    fitness_list = list()

    for ficheiro in files_list:
        fitness_list.append(fileSize(ficheiro))

    return fitness_list


def colorPalette(files_list):
    fitness_list = list()

    for ficheiro in files_list:
        try:
            fitness_list.append(contrasting_colours.fitness(ficheiro))
        except Exception as err:
            print(err, ficheiro)
            fitness_list.append(0)

    return fitness_list


def fractalDimension(files_list):
    return run_frac_lac(fitness_function='frac', files_list=files_list, csv_path='fitnessFrac.csv', del_file=True,
                        objective_value=1.5)


def lacunarity(files_list):
    return run_frac_lac('lac', files_list, 'fitnessLac.csv', True, 1.5)


def bell(files_list):
    return run_aesthetic('bell', files_list, 'fitnessBell.csv', True)


def complexity(files_list):
    return run_aesthetic('comp', files_list, 'fitnessComp.csv', True)


def tom_white(files_list):
    global ACTIVE_MODELS, IMAGENET_INDEXES
    fitness_list = []
    for ind in files_list:
        # print(ind)
        active_model_keys = sorted(ACTIVE_MODELS.keys())

        # build a table indexed by target_size for all resized image lists
        target_size_table = {}
        for k in active_model_keys:
            model = ACTIVE_MODELS[k]
            target_size = model.get_target_size()
            target_size_table[target_size] = []

        # build lists of images at all needed sizes
        # f_ = toolbox.compile(expr=ind)
        # img_array = image_generation(f_, img_width, img_height)  # TODO: Only square images now please!
        # img = Image.fromarray(img_array, 'RGB')
        img = Image.open(ind).convert('RGB')

        for target_size in target_size_table:
            if target_size is None:
                imr = img
            else:
                imr = img.resize(target_size, resample=Image.BILINEAR)
            target_size_table[target_size].append(np.asarray(imr))
        # print(target_size_table)
        # # convert all lists to np arrays
        for target_size in target_size_table:
            target_size_table[target_size] = np.array(target_size_table[target_size])

        # make all predictions
        full_predictions = []
        for k in active_model_keys:
            model = ACTIVE_MODELS[k]
            target_size = model.get_target_size()
            image_preprocessor = model.get_input_preprocessor()

            # images = target_size_table[target_size]
            images = np.copy(target_size_table[target_size])
            if image_preprocessor is not None:
                batch = image_preprocessor(images)
            else:
                batch = images
            preds = model.predict(batch)
            # print("PREDS:", preds.shape, preds)
            if isinstance(preds, dict) and "scores" in preds:
                # print(preds['scores'].shape)
                if (len(preds['scores'].shape) == 1):
                    worthy = preds['scores']
                elif preds['scores'].shape[1] == 1:
                    worthy = preds['scores']
                else:
                    worthy = preds['scores'][:, IMAGENET_INDEXES]
            else:
                worthy = preds[:, IMAGENET_INDEXES]
            # print("Worthy {}: {}".format(k, np.array(worthy).shape))
            full_predictions.append(worthy)

        # convert predictions to np array
        full_predictions = np.array(full_predictions)
        # if do_score_reverse:
        #   print("-> Applying predictions reversed")
        #   full_predictions = 1.0 - full_predictions
        top_classes = np.argmax(full_predictions, axis=2).flatten()
        top_class = np.argmax(np.bincount(top_classes))
        imagenet_index = IMAGENET_INDEXES[top_class]

        prediction_list = np.sum(full_predictions, axis=2)

        # extract rewards and merged
        rewards = np.prod(prediction_list, axis=0)
        merged = np.dstack(prediction_list)[0]
        # return rewards, [imagenet_index, merged]
        fitness_list.append(rewards[0])
    # print(rewards)
    return fitness_list


def CLIP(files_list):
    fitness_list = []
    for ind in files_list:
        pil_image = Image.open(ind).convert('RGB')

        fitness_value = CLIP_FITNESS(pil_image)

        fitness_list.append(fitness_value)

    return fitness_list


def evalFitness(pop_list, fitnessFunctionName, update_fitness):
    if fitnessFunctionName == 'sizePNG':
        fitnessFunction = size_png

    elif fitnessFunctionName == 'sizeJPG':
        fitnessFunction = size_jpg

    elif fitnessFunctionName == 'palette':
        fitnessFunction = colorPalette

    elif fitnessFunctionName == 'fractalDimension':
        fitnessFunction = fractalDimension

    elif fitnessFunctionName == 'lacunarity':
        fitnessFunction = lacunarity

    elif fitnessFunctionName == 'bell':
        fitnessFunction = bell

    elif fitnessFunctionName == 'complexity':
        fitnessFunction = complexity

    elif fitnessFunctionName == 'tomWhite':
        fitnessFunction = tom_white

    elif fitnessFunctionName == 'CLIP':
        fitnessFunction = CLIP

    files_list = list()
    renderings_list = list()

    for render in pop_list:
        # TODO - this fitnesses
        if fitnessFunctionName == 'lacunarity' or fitnessFunctionName == 'fractalDimension':
            a = 2
        # TODO: stuff - blackandwhite
        # rgba = calcParameters(member.background)
        # files_list.append(member.fileName.split('.cfdg')[0]+'.png'+rgba)
        # END OF TODO
        else:
            files_list.append(render.dir)
            renderings_list.append(render)

    fitness_list = fitnessFunction(files_list)

    if update_fitness:
        for index in range(len(fitness_list)):
            renderings_list[index].fitness = fitness_list[index]
    else:
        for index in range(len(fitness_list)):
            renderings_list[index].fitness_dict[fitnessFunctionName] = fitness_list[index]


def multipleFitnessFunction(pop_list, fitnesses, weights):
    for fitness in fitnesses:
        evalFitness(pop_list, fitness, False)

    for idx_pop in range(len(pop_list)):
        fit = 0
        for idx_fit in range(len(fitnesses)):
            fit += weights[idx_fit] * pop_list[idx_pop].fitness_dict[fitnesses[idx_fit]]
        pop_list[idx_pop].fitness = fit


def classifyFitness(pop_list, fitness_functions, update_fitness):
    to_calc = list()
    fitness_statistics_list = list()
    for fitness_function in fitness_functions:
        for member in pop_list:
            for render in member.renderings:
                file_size = fileSize(render.dir)

                if file_size == 0:
                    if update_fitness:
                        render.fitness = 0
                    else:
                        render.fitness_dict[fitness_function] = 0
                else:
                    to_calc.append(render)

        # TODO - fix this
        if update_fitness and len(fitness_functions) > 1:
            multipleFitnessFunction(to_calc, fitness_functions, [0.5, 0.5])

        else:
            evalFitness(to_calc, fitness_function, update_fitness)

    for fitness_function in fitness_functions:
        for member in pop_list:
            value = 0.0
            for render in member.renderings:
                if update_fitness:
                    value += render.fitness
                else:
                    value += render.fitness_dict[fitness_function]

            fit = float(value) / len(member.renderings)

            if update_fitness:
                member.fitness = fit
            else:
                member.fitness_dict[fitness_function] = fit
