import networkx as nx
import numpy as np
import os
import lingam
import sys
# from lingam.utils import make_dot, print_causal_directions, print_dagc

def causal_discovery_varlingam(data, lag):
    model = lingam.VARLiNGAM(lags=lag)
    model.fit(data)
    summary_matrix = np.sum(np.abs(model.adjacency_matrices_), axis=0)
    causal_graph = nx.from_numpy_array(summary_matrix.T, create_using=nx.DiGraph)
    for u, v, d in causal_graph.edges(data=True):
        del d['weight']
    return causal_graph

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: data_file num_lags market_name algorithm')
        exit()
        
    output_directory = "./causal_graphs"
    os.makedirs(output_directory, exist_ok=True)

    data_filename = sys.argv[1]
    num_lags = int(sys.argv[2])
    market_name = sys.argv[3]
    algorithm = sys.argv[4]

    data = np.genfromtxt(data_filename, delimiter=',', skip_header=1)
    print('Running', market_name, num_lags, algorithm)
    G = causal_discovery_varlingam(data, num_lags)
    output_filename = os.path.join(output_directory, f'{market_name}_graph_{algorithm}_lag_{num_lags}.txt')
    nx.write_adjlist(G, output_filename)
