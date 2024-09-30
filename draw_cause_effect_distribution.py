import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

def filter_G(summary_matrix, percent):
    G = nx.from_numpy_array(summary_matrix.T, create_using=nx.DiGraph)
    percentile = np.percentile(summary_matrix, percent)
    G_filtered = G.copy()
    for u, v, data in list(G_filtered.edges(data=True)):
        if data.get('weight', 0) < percentile:
            G_filtered.remove_edge(u, v)
    return G_filtered

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print('Usage: summary_matrix_file percent algorithm market lag cause_step effect_step')
        sys.exit()

    output_directory = "./plots"
    os.makedirs(output_directory, exist_ok=True)

    summary_matrix_file = sys.argv[1]
    percent = float(sys.argv[2])
    algorithm = sys.argv[3]
    market = sys.argv[4]
    lag = int(sys.argv[5])
    cause_step = int(sys.argv[6])
    effect_step = int(sys.argv[7])

    summary_matrix = np.genfromtxt(summary_matrix_file, delimiter=',', dtype=None, encoding=None)
    G_filtered = filter_G(summary_matrix, percent)

    cause_counts = {}
    for node in G_filtered.nodes():
        cause_counts[node] = G_filtered.in_degree(node)
    cause_counts_list = list(cause_counts.values())

    plt.figure(figsize=(5, 3))
    sns.histplot(cause_counts_list, kde=False)
    plt.xticks(np.arange(min(cause_counts_list), max(cause_counts_list) + 1, cause_step))
    plt.xlabel('Number of Causes')
    plt.ylabel('Frequency')
    plt.tight_layout()
    cause_file_name = os.path.join(output_directory, f'{market}_cause_distribution_{algorithm}_lag_{lag}_{percent}_percentile.pdf')
    plt.savefig(cause_file_name)

    effect_counts = {}
    for node in G_filtered.nodes():
        effect_counts[node] = G_filtered.out_degree(node)
    effect_counts_list = list(effect_counts.values())

    plt.figure(figsize=(5, 3))
    sns.histplot(effect_counts_list, kde=False)
    plt.xticks(np.arange(min(effect_counts_list), max(effect_counts_list) + 1, effect_step))
    plt.xlabel('Number of Effects')
    plt.ylabel('Frequency')
    plt.tight_layout()
    effect_file_name = os.path.join(output_directory, f'{market}_effect_distribution_{algorithm}_lag_{lag}_{percent}_percentile.pdf')
    plt.savefig(effect_file_name)
   