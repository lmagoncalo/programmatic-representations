import os

import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
from matplotlib import pyplot as plt

prompts = ["sunset, bright colors", "balloons", "smiley"]


def collect_cgp_stats():
    rootdir = './cgp/runs'
    all_fitnesses = []

    # Iterate over files in directory
    for folder in os.listdir(rootdir):
        if folder != ".DS_Store":
            stats_file = f'{rootdir}/{folder}/pop_stats.csv'

            if os.path.isfile(stats_file):
                # print(stats_file)
                df = pd.read_csv(stats_file)
                fitnesses = df['best_fitness'].values.tolist()

                all_fitnesses.append(fitnesses)

    print(len(all_fitnesses))

    # Calculate average from 10 lists
    avg_first = np.array(all_fitnesses[:10]).mean(axis=0)
    avg_second = np.array(all_fitnesses[10:20]).mean(axis=0)
    avg_third = np.array(all_fitnesses[20:]).mean(axis=0)

    averages = [avg_first, avg_second, avg_third]

    generations = list(range(len(all_fitnesses[0])))

    index = 0
    for i in range(3):
        plt.figure()
        for j in range(10):
            plt.plot(generations, all_fitnesses[index], label=f"Run {j}", color="red", alpha=0.4)
            index += 1

        plt.plot(generations, averages[i], label="Average", color="black")

        red_patch = mpatches.Patch(color='red', label='Fitnesses of 10 runs')
        blue_patch = mpatches.Patch(color='black', label='Average Fitness')

        plt.legend(handles=[red_patch, blue_patch])

        # Adding title and labels
        plt.title('Fitness (CGP), Prompt: ' + prompts[i])
        plt.xlabel('Generations')
        plt.ylabel('Fitness Value')

        plt.savefig("./stats/cgp_" + prompts[i].replace(",", "").replace(" ", "_") + ".png")


def collect_gp_stats():
    rootdir = './gp/runs/emlart-gp'
    all_fitnesses = []

    # Iterate over files in directory
    for folder in os.listdir(rootdir):
        if folder != ".DS_Store":
            stats_file = f'{rootdir}/{folder}/evolution_{folder}.csv'

            if os.path.isfile(stats_file):
                df = pd.read_csv(stats_file)
                fitnesses = df['fitness_generational_best'].values.tolist()

                fitnesses = fitnesses[:501]

                all_fitnesses.append(fitnesses)

    print(len(all_fitnesses))

    # Calculate average from 10 lists
    avg_first = np.array(all_fitnesses[:10]).mean(axis=0)
    avg_second = np.array(all_fitnesses[10:20]).mean(axis=0)
    avg_third = np.array(all_fitnesses[20:]).mean(axis=0)

    averages = [avg_first, avg_second, avg_third]

    generations = list(range(len(all_fitnesses[0])))

    index = 0
    for i in range(3):
        plt.figure()
        for j in range(10):
            plt.plot(generations, all_fitnesses[index], label=f"Run {j}", color="red", alpha=0.4)
            index += 1

        plt.plot(generations, averages[i], label="Average", color="black")

        red_patch = mpatches.Patch(color='red', label='Fitnesses of 10 runs')
        blue_patch = mpatches.Patch(color='black', label='Average Fitness')

        plt.legend(handles=[red_patch, blue_patch])

        # Adding title and labels
        plt.title('Fitness (GP), Prompt: ' + prompts[i])
        plt.xlabel('Generations')
        plt.ylabel('Fitness Value')

        plt.savefig("./stats/gp_" + prompts[i].replace(",", "").replace(" ", "_") + ".png")


def collect_cfdg_stats():
    pass


def collect_neat_stats():
    rootdir = './neat/runs'
    all_fitnesses = []

    # Iterate over files in directory
    for folder in os.listdir(rootdir):
        if folder != ".DS_Store":
            stats_file = f'{rootdir}/{folder}/stats.csv'

            if os.path.isfile(stats_file):
                df = pd.read_csv(stats_file)
                fitnesses = df['Max Fitness'].values.tolist()

                all_fitnesses.append(fitnesses)

    print(len(all_fitnesses))

    def tolerant_mean(arrs):
        lens = [len(i) for i in arrs]
        arr = np.ma.empty((np.max(lens), len(arrs)))
        arr.mask = True
        for idx, l in enumerate(arrs):
            arr[:len(l), idx] = l
        return arr.mean(axis=-1)

    # Calculate average from 10 lists
    avg_first = tolerant_mean(all_fitnesses[:10])
    avg_second = tolerant_mean(all_fitnesses[10:20])
    # avg_third = tolerant_mean(all_fitnesses[20:])

    # averages = [avg_first, avg_second, avg_third]
    averages = [avg_first, avg_second]

    index = 0
    for i in range(3):
        plt.figure()
        for j in range(10):
            generations = list(range(len(all_fitnesses[index])))
            plt.plot(generations, all_fitnesses[index], label=f"Run {j}", color="red", alpha=0.4)
            index += 1

            if index >= len(all_fitnesses):
                break

        generations = list(range(len(averages[i])))
        plt.plot(generations, averages[i], label="Average", color="black")

        red_patch = mpatches.Patch(color='red', label='Fitnesses of 10 runs')
        blue_patch = mpatches.Patch(color='black', label='Average Fitness')

        plt.legend(handles=[red_patch, blue_patch])

        # Adding title and labels
        plt.title('Fitness (NEAT), Prompt: ' + prompts[i])
        plt.xlabel('Generations')
        plt.ylabel('Fitness Value')

        plt.savefig("./stats/neat_" + prompts[i].replace(",", "").replace(" ", "_") + ".png")

        if index >= len(all_fitnesses):
            break


def main():
    collect_cgp_stats()
    collect_gp_stats()
    collect_cfdg_stats()
    collect_neat_stats()


if '__main__' == __name__:
    main()
