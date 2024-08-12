import numpy as np
import pandas as pd
import networkx as nx
import os

def string_nodes(nodes):
    new_nodes = []
    for col in nodes:
        try:
            int(col)
            new_nodes.append("V" + str(col))
        except ValueError:
            new_nodes.append(col)
    return new_nodes

def ts_fci_dataframe_to_dict(df, names, nlags):
    # todo: check if its correct
    for i in range(df.shape[1]):
        for j in range(i+1, df.shape[1]):
            if df[df.columns[i]].loc[df.columns[j]] == 2:
                if df[df.columns[j]].loc[df.columns[i]] == 2:
                    print(df.columns[i] + " <-> " + df.columns[j])

    g_dict = dict()
    for name_y in names:
        g_dict[name_y] = []
    for ty in range(nlags):
        for name_y in names:
            t_name_y = df.columns[ty*len(names)+names.index(name_y)]
            for tx in range(nlags):
                for name_x in names:
                    t_name_x = df.columns[tx * len(names) + names.index(name_x)]
                    if df[t_name_y].loc[t_name_x] == 2:
                        if (name_x, tx-ty) not in g_dict[name_y]:
                            g_dict[name_y].append((name_x, tx - ty))
                    # if (name_x, ty - tx, ">") not in g_dict[name_y]:
                    #     g_dict[name_y].append((name_x, ty-tx, ">"))
                    # elif df[t_name_y].loc[t_name_x] == 3:
                    #     if (name_x, ty - tx, "o") not in g_dict[name_y]:
                    #         g_dict[name_y].append((name_x, ty - tx, "o"))
    # print(g_dict)
    return g_dict

def dict_to_tgraph(nodes, temporal_dict):
    tgraph = nx.DiGraph()
    tgraph.add_nodes_from(nodes)

    for name_y in temporal_dict.keys():
        for name_x, t_xy in temporal_dict[name_y]:
            if (name_x, name_y) in tgraph.edges:
                tgraph.edges[name_x, name_y]['time'].append(-t_xy)
            else:
                if name_x not in tgraph.nodes or name_y not in tgraph.nodes:
                    print(f"Adding edge ({name_x}, {name_y}) which is not in initial nodes")
                tgraph.add_edges_from([(name_x, name_y)])
                tgraph.edges[name_x, name_y]['time'] = [-t_xy]
    
    return tgraph

def tgraph_to_graph(tg):
    g = nx.DiGraph()
    og = nx.DiGraph()
    g.add_nodes_from(tg.nodes)
    og.add_nodes_from(tg.nodes)
    for cause, effects in tg.adj.items():
        for effect, _ in effects.items():
            if cause != effect:
                og.add_edges_from([(cause, effect)])
                g.add_edges_from([(cause, effect)])
            else:
                g.add_edges_from([(cause, effect)])
    return g, og



nlags = 5

# data = pd.read_csv('./data/Cleaned_nancy_data.csv', delimiter=',', index_col=False, header=0)
# col_num = data.shape[1]
# nodes = [i for i in range(col_num)]

nodes = [i for i in range(5)]
tsfci_result_df = pd.read_csv('tsfci_result_1.csv', header=0, index_col=0)

tsfci_dict = ts_fci_dataframe_to_dict(tsfci_result_df, nodes, nlags)
tsfci_tgraph = dict_to_tgraph(nodes, tsfci_dict)
G, _ = tgraph_to_graph(tsfci_tgraph)

output_directory = "./causal_graphs"
market_name = 'nancy'
num_lags = nlags-1
output_filename = os.path.join(output_directory, f'{market_name}_graph_tsfci_lag_{num_lags}.txt')
nx.write_adjlist(G, output_filename)