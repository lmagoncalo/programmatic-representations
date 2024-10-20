import random
import sys

import clip
import numpy as np
import torch
import torchvision.transforms.functional as TF
from PIL import Image

import utils
from evolution import generate
from laion_aesthetics import init_laion

# device for the clip and aesthetic model
device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
aesthetic_model, vit_model, preprocess = init_laion(device)

prompt = sys.argv[3]  # e.g. "sunset, bright colors"
text_inputs = clip.tokenize(prompt).to(device)
with torch.no_grad():
    text_features = vit_model.encode_text(text_inputs)

def clip(population):
    for indi_i in range(len(population)):
        image_numpy = population[indi_i].data

        pil_image = Image.fromarray((image_numpy * 1).astype(np.uint8))

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

        # 1 - just similarity between image features and text features
        ind_fitness = similarity.item()

        population[indi_i].fitness = ind_fitness

    return population


def main():
    initial_seed = int(sys.argv[1])
    number_generations = int(sys.argv[2])

    configs = utils.load_configs("configs.json")

    configs['max_generation'] = number_generations

    random.seed(initial_seed)
    np.random.seed(initial_seed)
    input_img = utils.create_white_img(configs['image_width'], configs['image_height'])
    generate(configs, clip, input_img)


if __name__ == '__main__':
    main()
