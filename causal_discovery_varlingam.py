import networkx as nx
import numpy as np
import os
import lingam
import sys
import pandas as pd

def causal_discovery_varlingam(data, lag):
    model = lingam.VARLiNGAM(lags=lag)
    model.fit(data)
    summary_matrix = np.sum(np.abs(model.adjacency_matrices_), axis=0)   # weight calculation method may be changed later
    causal_graph = nx.from_numpy_array(summary_matrix.T, create_using=nx.DiGraph)
    # for u, v, d in causal_graph.edges(data=True):
    #     del d['weight']
    return causal_graph, summary_matrix

def find_major_causes(G, target_node, num_causes):
    parent_weights = []
    for parent in G.predecessors(target_node):
        weight = G[parent][target_node]['weight']
        parent_weights.append((parent, weight))
    top_parents = sorted(parent_weights, key=lambda x: x[1], reverse=True)[:num_causes]
    major_causes = [parent for parent, weight in top_parents]
    while len(major_causes) < num_causes:
        major_causes.append(None)
    return major_causes


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: data_file num_lags market_name algorithm')
        # print('Usage: data_file num_lags market_name algorithm num_causes')
        exit()
        
    output_directory = "./causal_graphs"
    os.makedirs(output_directory, exist_ok=True)

    data_filename = sys.argv[1]
    num_lags = int(sys.argv[2])
    market_name = sys.argv[3]
    algorithm = sys.argv[4]
    # num_causes = int(sys.argv[5])

    data = np.genfromtxt(data_filename, delimiter=',', skip_header=1)
    print('Running', market_name, num_lags, algorithm)
    G, summary_matrix = causal_discovery_varlingam(data, num_lags)
    output_filename = os.path.join(output_directory, f'{market_name}_graph_{algorithm}_lag_{num_lags}.txt')
    nx.write_adjlist(G, output_filename)
    matrix_filename = os.path.join(output_directory, f'{market_name}_summary_matrix_{algorithm}_lag_{num_lags}.csv')
    np.savetxt(matrix_filename, summary_matrix, delimiter=',')


    # all_major_causes = []
    # for target_node in range(G.number_of_nodes()):
    #     major_causes = find_major_causes(G, target_node, num_causes)
    #     major_causes.insert(0, target_node)
    #     new_row = major_causes
    #     all_major_causes.append(new_row)
    # tickers = pd.read_csv(data_filename, delimiter=',', nrows=1).columns.to_list()
    # for i in range(len(all_major_causes)):
    #     for j in range(len(all_major_causes[i])):
    #         if all_major_causes[i][j] is not None:
    #             all_major_causes[i][j] = tickers[all_major_causes[i][j]]
    # causes_filename = os.path.join(output_directory, f'{market_name}_major_causes_{algorithm}_lag_{num_lags}.txt')
    # np.savetxt(causes_filename, all_major_causes, fmt='%s', delimiter=', ')
    # print('Major causes saved', market_name, num_lags, algorithm)