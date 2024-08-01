import networkx as nx
import numpy as np
import pandas as pd
import os
import lingam
from lingam.utils import make_dot, print_causal_directions, print_dagc

def causal_discovery_varlingam(data, lag):
    model = lingam.VARLiNGAM(lags=lag)
    model.fit(data)
    summary_matrix = np.sum(np.abs(model.adjacency_matrices_), axis=0)
    causal_graph = nx.from_numpy_array(summary_matrix.T, create_using=nx.DiGraph)
    for u, v, d in causal_graph.edges(data=True):
            del d['weight']
    return causal_graph

def causal_discovery(data, lag_range, market_name, algorithm):
    directory = "./causal_graph"
    os.makedirs(directory, exist_ok=True)
    for i in lag_range:
        print(f"lag={i}")
        if algorithm == "varlingam":
            G = causal_discovery_varlingam(data, i)
        filename = os.path.join(directory, f'{market_name}_graph_{algorithm}_lag_{i}.txt')
        nx.write_adjlist(G, filename)

data = pd.read_csv('./data/Cleaned_S_P_500_Data.csv', delimiter=',', index_col=False, header=0)
data = data.to_numpy()
causal_discovery(data, range(1,6), "sp500", "varlingam")
