import sys
import csv
from statistics import mean

import cgp  # From: https://github.com/Happy-Algorithms-League/hal-cgp
import clip
import numpy as np
import torch
from torchvision.utils import save_image
from PIL import Image

import utils
from laion_aesthetics import init_laion


# device for the clip and aesthetic model
device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
aesthetic_model, vit_model, preprocess = init_laion(device)

prompt = sys.argv[3]  # e.g. "sunset, bright colors"
text_inputs = clip.tokenize(prompt).to(device)
with torch.no_grad():
    text_features = vit_model.encode_text(text_inputs)

max_fitnesses = []
min_fitnesses = []
avg_fitnesses = []


def get_input_matrix(min_value, max_value, num_rows, num_columns, num_rotations):
    matrix = np.linspace(min_value, max_value, num=num_rows)
    matrix = np.resize(matrix, num_rows * num_columns)
    matrix = np.reshape(matrix, (num_rows, num_columns))
    matrix = np.rot90(matrix, k=num_rotations)

    return matrix


def objective(individual):
    if not individual.fitness_is_None():
        return individual

    num_rows = 224
    num_columns = 224
    num_outputs = 3

    output = np.zeros((num_outputs, num_rows, num_columns))

    f = individual.to_func()

    x_values = get_input_matrix(-1.0, 1.0, num_rows, num_columns, 0)
    y_values = get_input_matrix(-1.0, 1.0, num_rows, num_columns, 1)
    input_data = np.array((x_values, y_values))

    for i in range(num_rows):
        for j in range(num_columns):
            output[:, i, j] = f(input_data[0, i, j], input_data[1, i, j])

    for k in range(num_outputs):
        output[k, :, :] = np.interp(output[k, :, :], [0.0, 1.0], [0.0, 255.0])

    output = output.reshape((num_rows, num_columns, num_outputs))

    pil_image = Image.fromarray((output * 1).astype(np.uint8))

    image = preprocess(pil_image).unsqueeze(0).to(device)

    individual.data = image

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

    # 1 - just similarity between image features and text features
    ind_fitness = similarity.item()

    individual.fitness = ind_fitness

    return individual


def recording_callback(population):
    fitness_list = population.fitness_parents()

    max_fitnesses.append(max(fitness_list))
    min_fitnesses.append(min(fitness_list))
    avg_fitnesses.append(mean(fitness_list))

    save_image(population.champion.data, output_folder + "/individual_" + str(population.generation) + "_" + str(population.champion.fitness) + ".png")


genome_params = {
    "n_inputs": 2,
    "n_outputs": 3,
    "n_columns": 50,  # 10
    "n_rows": 1,  # 5
    "levels_back": 5,
    "primitives": (cgp.Add, cgp.Sub, cgp.Mul, cgp.ConstantFloat, cgp.Parameter),
}

initial_seed = int(sys.argv[1])
number_generations = int(sys.argv[2])

output_folder = f"runs/cgp_{prompt.replace(' ', '_')}_{initial_seed}"
utils.create_directory(output_folder)

population_params = {"n_parents": 20, "seed": initial_seed}
evolve_params = {"max_generations": number_generations, "termination_fitness": 1.0}
ea_params = {"n_offsprings": 50, "tournament_size": 4, "mutation_rate": 0.15}

pop = cgp.Population(**population_params, genome_params=genome_params)
ea = cgp.ea.MuPlusLambda(**ea_params)

cgp.evolve(objective, pop, ea, **evolve_params, print_progress=True, callback=recording_callback)

rows = zip(range(0, number_generations), max_fitnesses, min_fitnesses, avg_fitnesses)

with open(f"{output_folder}/stats.csv", "w") as f:
    headernames = ["Generation", "Max Fitness", "Min Fitness", "Avg Fitness"]
    writer = csv.writer(f)
    writer.writerow(headernames)
    for row in rows:
        writer.writerow(row)

