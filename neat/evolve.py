import datetime

import os
import shutil
import sys

import clip
import numpy as np
import torch
from PIL import Image

import neat
from laion_aesthetics import init_laion

# device for the clip and aesthetic model
device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
aesthetic_model, vit_model, preprocess = init_laion(device)

# Process the prompt, only needed once!
prompt = sys.argv[3]  # e.g. "sunset, bright colors"
text_inputs = clip.tokenize(prompt).to(device)
with torch.no_grad():
    text_features = vit_model.encode_text(text_inputs)


def eval_color_image(genome, config, width, height):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    image = []
    for r in range(height):
        y = -1.0 + 2.0 * r / (height - 1)
        row = []
        for c in range(width):
            x = -1.0 + 2.0 * c / (width - 1)
            output = net.activate([x, y])
            red = int(round((output[0] + 1.0) * 255 / 2.0))
            green = int(round((output[1] + 1.0) * 255 / 2.0))
            blue = int(round((output[2] + 1.0) * 255 / 2.0))
            red = max(0, min(255, red))
            green = max(0, min(255, green))
            blue = max(0, min(255, blue))
            row.append((red, green, blue))
        image.append(row)

    image = np.array(image)

    return image

# NEAT individual evaluation
def image_evaluation(genomes, config):
    best_fitness = float('-inf')

    for n, (genome_id, genome) in enumerate(genomes):
        image_numpy = eval_color_image(genome, config, 224, 224)
        
        # preprocess the image to be used in Clip image model (ViT)
        pil_image = Image.fromarray((image_numpy * 1).astype(np.uint8))

        # Save image
        # pil_image.save(f"{save_path}images/all/generation_{pop.generation:05d}/gen{pop.generation:05d}_ind{n:05d}.png")

        image = preprocess(pil_image).unsqueeze(0).to(device)

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
        
        ##### fitness assignment!
        # 1 - just similarity between image features and text features
        ind_fitness = similarity.item()
        
        # 2 - just aesthetics
        #ind_fitness = aesthetic_eval_laion 
        
        # 3 - combined. aesthetics is in range of values 
        # and so to compensate we will divide by a constant the aesthetic response
        #ind_fitness = similarity.item() + aesthetic_eval_laion/200.0

        # check and update best individual
        if ind_fitness > best_fitness:
            best_fitness = ind_fitness
            best_ind = pil_image

        genome.fitness = ind_fitness

    # Save best
    best_ind.save(f"{save_path}images/best/best_gen{pop.generation:05d}.png")

    print("Best Fitness:", best_fitness)


if __name__ == "__main__":
    # device definition for TensorGP
    dev = "gpu:0"  # '/gpu:0'  # device to run, write '/cpu_0' to run on cpu
    # when converting from genotype to phenotype 
    # we will be creating an individual at the following resolution
    image_resolution = [224, 224, 3]
    # some EC related params
    initial_seed = int(sys.argv[1])
    number_generations = int(sys.argv[2])

    config_path = 'interactive_config_color'

    # Note that we provide the custom stagnation class to the Config constructor.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    config.pop_size = 100
    pop = neat.Population(config)

    print("Evolving with the prompt:", sys.argv[4])

    date = datetime.datetime.utcnow().strftime('%Y_%m_%d__%H_%M_%S_%f')[:-3]
    # define the name of the directory with its subdirectories
    save_path = f'runs/run_{date}/'
    os.makedirs(save_path + "images/all", exist_ok=True)
    os.makedirs(save_path + "images/best", exist_ok=True)

    # Copy configuration
    shutil.copy(config_path, save_path + config_path)

    for _ in range(number_generations):
        print(f"Generation: {pop.generation}")
        # Create generation folder
        os.makedirs(f"{save_path}images/all/generation_{pop.generation:05d}", exist_ok=True)

        pop.run(image_evaluation, 1)    

