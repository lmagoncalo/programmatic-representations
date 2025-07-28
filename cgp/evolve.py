import os
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


class Sin(cgp.OperatorNode):
    """Nó que calcula o seno do seu único input."""
    _arity = 1
    _def_output       = "math.sin(x_0)"
    _def_numpy_output = "np.sin(x_0)"
    _def_torch_output = "torch.sin(x_0)"
    _def_sympy_output = "sin(x_0)"


# device for the clip and aesthetic model
device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
aesthetic_model, vit_model, preprocess = init_laion(device)

# Load config
config = utils.load_configs("configs.json")

# CLI args
initial_seed    = int(sys.argv[1])
number_gens     = int(sys.argv[2])
prompt          = sys.argv[3]
output_folder_root = config["output_folder_root"]

output_folder = f"{output_folder_root}/cgp_{prompt.replace(' ', '_')}_{initial_seed}"
utils.create_directory(output_folder)

image_settings = config["image_settings"]
genome_config = config["genome_params"]
population_config = config["population_params"]
evolution_config = config["evolution_params"]

max_fitnesses = []
min_fitnesses = []
avg_fitnesses = []

text_inputs = clip.tokenize(prompt).to(device)
with torch.no_grad():
    text_features = vit_model.encode_text(text_inputs)


def get_input_matrix(min_value, max_value, width, height, num_rotations):
    matrix = np.linspace(min_value, max_value, num=width)
    matrix = np.resize(matrix, width * height)
    matrix = np.reshape(matrix, (width, height))
    matrix = np.rot90(matrix, k=num_rotations)

    return matrix


def objective(individual):
    if not individual.fitness_is_None():
        return individual

    width = image_settings["width"]
    height = image_settings["height"]
    channels = image_settings["channels"]

    output = np.zeros((channels, width, height), dtype=np.float32)

    f = individual.to_func()

    x_values = get_input_matrix(-1.0, 1.0, width, height, 0)
    y_values = get_input_matrix(-1.0, 1.0, width, height, 1)
    input_data = np.array((x_values, y_values))

    for i in range(width):
        for j in range(height):
            output[:, i, j] = f(input_data[0, i, j], input_data[1, i, j])

    for k in range(channels):
        output[k, :, :] = np.interp(output[k, :, :], [0.0, 1.0], [0.0, 255.0])

    pil_image = Image.fromarray(output.transpose(1,2,0).astype(np.uint8))

    tensor = preprocess(pil_image).unsqueeze(0).to(device)

    individual.data = tensor

    # extract the image features from the clip vit encoding
    with torch.no_grad():
        image_features = vit_model.encode_image(tensor)
    # im_emb_arr = normalizer(image_features.cpu().detach().numpy())
    # get aesthetic prediction from the laion model
    # prediction = aesthetic_model(torch.from_numpy(im_emb_arr).to(device).type(torch.float))
    # aesthetic_eval_laion = prediction.item()

    # calculate the cosine similarity between the text features
    # of the prompt and the image features of the current individual
    similarity = torch.cosine_similarity(text_features, image_features, dim=-1).mean().item()

    individual.fitness = similarity

    return individual


def recording_callback(population):
    fitness_list = population.fitness_parents()

    max_fitnesses.append(max(fitness_list))
    min_fitnesses.append(min(fitness_list))
    avg_fitnesses.append(mean(fitness_list))

    # make a per-generation folder
    gen_dir = os.path.join(output_folder, f"gen_{population.generation:03d}")
    os.makedirs(gen_dir, exist_ok=True)

    # also save the champion at top level
    save_image(
        population.champion.data,
        os.path.join(output_folder, f"champ_{population.generation:03d}_{population.champion.fitness:.4f}.png")
    )

    # dump per-gen fitness CSV
    with open(os.path.join(gen_dir, "fitness.csv"), "w", newline="") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["idx", "fitness"])
        for idx, fit in enumerate(fitness_list):
            writer.writerow([idx, fit])


genome_params = {
    "n_inputs": genome_config["n_inputs"],
    "n_outputs": genome_config["n_outputs"],
    "n_columns": genome_config["n_columns"],
    "n_rows": genome_config["n_rows"],
    "levels_back": genome_config["levels_back"],
    "primitives": (cgp.Add, cgp.Sub, cgp.Mul, cgp.ConstantFloat, cgp.Parameter, Sin),
}


population_params = {
    "n_parents": population_config["n_parents"],
    "seed": initial_seed
}

evolve_params = {
    "max_generations": evolution_config["max_generations"],
    "termination_fitness": evolution_config["termination_fitness"]
}

ea_params = {
    "n_offsprings": evolution_config["n_offsprings"],
    "tournament_size": evolution_config["tournament_size"],
    "mutation_rate": evolution_config["mutation_rate"]
}

pop = cgp.Population(**population_params, genome_params=genome_params)
ea = cgp.ea.MuPlusLambda(**ea_params)

cgp.evolve(objective, pop, ea, **evolve_params, print_progress=True, callback=recording_callback)

rows = zip(range(0, number_gens), max_fitnesses, min_fitnesses, avg_fitnesses)

# Finally dump stats.csv
with open(os.path.join(output_folder, "stats.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Generation", "Max Fitness", "Min Fitness", "Avg Fitness"])
    for gen, mx, mn, av in zip(range(number_gens), max_fits, min_fits, avg_fits):
        writer.writerow([gen, mx, mn, av])

