import argparse
import random

import numpy as np
import torch
import torchvision.transforms.functional as TF
import clip

import utils
from laion_aesthetics import init_laion
from evolution import generate

# device for the clip and aesthetic model
device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
aesthetic_model, vit_model, preprocess = init_laion(device)

prompt = "sunset, bright colors"

text_inputs = clip.tokenize(prompt).to(device)
with torch.no_grad():
    text_features = vit_model.encode_text(text_inputs)


def clip(population):
    for indi_i in range(len(population)):
        image = population[indi_i].data.astype(np.uint8)
        image = TF.to_tensor(image).unsqueeze(0)  # .unsqueeze(0)#TF.to_tensor(x).unsqueeze(0)

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

        population[indi_i].fitness = ind_fitness
    return population


def main():
    description = "Cartesian Genetic Programming"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--config', metavar='config', type=str, help='Configs file')
    parser.add_argument('--random-seed', metavar="random_seed", type=int, help='Random seed')
    parser.add_argument('--max-gens', metavar="max_gens", type=int, help='Maximum number of generations')
    parser.add_argument('--save-folder', metavar="save_folder", type=str, help='Root output folder')
    args = parser.parse_args()

    args.config = "configs_clip.json"
    args.random_seed = 43
    args.save_folder = "outputs"
    args.max_gens = 30

    # print(args)

    configs = utils.load_configs(args.config)
    configs["max_generation"] = args.max_gens
    configs["save_folder"] = args.save_folder

    random.seed(args.random_seed)
    input_img = utils.create_white_img(configs['image_width'], configs['image_height'])
    generate(configs, clip, input_img)


if __name__ == '__main__':
    main()
