from tigramite import data_processing as pp
from tigramite.pcmci import PCMCI
from tigramite.independence_tests.parcorr import ParCorr
import numpy as np
import networkx as nx
import sys
import os

def causal_discovery_pcmci(data, lag, cond_ind_test=ParCorr()):
    nodes = [i for i in range(data.shape[1])]
    data_tigramite = pp.DataFrame(data)
    pcmci = PCMCI(dataframe=data_tigramite, cond_ind_test=cond_ind_test)
    pcmci.run_pcmci(tau_max=lag)
    res_dict = pcmci.all_parents
    # res_dict = dict()
    # for effect in pcmci.all_parents.keys():
    #     res_dict[pcmci.var_names[effect]] = []
    #     for cause, t in pcmci.all_parents[effect]:
    #         res_dict[pcmci.var_names[effect]].append((pcmci.var_names[cause], t))
    # pcmci_tgraph = dict_to_tgraph(nodes, res_dict)
    # causal_graph, _ = tgraph_to_graph(pcmci_tgraph)
    causal_graph = nx.DiGraph()
    causal_graph.add_nodes_from(nodes)
    for node in causal_graph.nodes():
        causal_graph.add_edge(node, node)
    for effect in res_dict:
        for cause, _ in res_dict[effect]:
            causal_graph.add_edges_from([(cause, effect)])
    return causal_graph

# def dict_to_tgraph(nodes, temporal_dict):
#     tgraph = nx.DiGraph()
#     tgraph.add_nodes_from(nodes)

#     for name_y in temporal_dict.keys():
#         for name_x, t_xy in temporal_dict[name_y]:
#             if (name_x, name_y) in tgraph.edges:
#                 tgraph.edges[name_x, name_y]['time'].append(-t_xy)
#             else:
#                 if name_x not in tgraph.nodes or name_y not in tgraph.nodes:
#                     print(f"Adding edge ({name_x}, {name_y}) which is not in initial nodes")
#                 tgraph.add_edges_from([(name_x, name_y)])
#                 tgraph.edges[name_x, name_y]['time'] = [-t_xy]
    
#     return tgraph

# def tgraph_to_graph(tg):
#     g = nx.DiGraph()
#     og = nx.DiGraph()
#     g.add_nodes_from(tg.nodes)
#     og.add_nodes_from(tg.nodes)
#     for cause, effects in tg.adj.items():
#         for effect, _ in effects.items():
#             if cause != effect:
#                 og.add_edges_from([(cause, effect)])
#                 g.add_edges_from([(cause, effect)])
#             else:
#                 g.add_edges_from([(cause, effect)])
#     return g, og


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
    G = causal_discovery_pcmci(data, num_lags)
    output_filename = os.path.join(output_directory, f'{market_name}_graph_{algorithm}_lag_{num_lags}.txt')
    nx.write_adjlist(G, output_filename)