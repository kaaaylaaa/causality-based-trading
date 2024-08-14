import numpy as np
import pandas as pd
import networkx as nx
import graphviz
import lingam
from lingam.utils import make_dot, print_causal_directions, print_dagc

np.set_printoptions(precision=3, suppress=True)
np.random.seed(0)


def string_nodes(nodes):
    new_nodes = []
    for col in nodes:
        try:
            int(col)
            new_nodes.append("V" + str(col))
        except ValueError:
            new_nodes.append(col)
    return new_nodes


def tgraph_to_graph(tg):
    g = nx.DiGraph()
    og = nx.DiGraph()
    sg = nx.DiGraph()
    g.add_nodes_from(tg.nodes)
    og.add_nodes_from(tg.nodes)
    sg.add_nodes_from(tg.nodes)
    for cause, effects in tg.adj.items():
        for effect, _ in effects.items():
            if cause != effect:
                og.add_edges_from([(cause, effect)])
                g.add_edges_from([(cause, effect)])
            else:
                sg.add_edges_from([(cause, effect)])
                g.add_edges_from([(cause, effect)])
    return g, og, sg


def three_col_format_to_graphs(nodes, three_col_format):
    tgtrue = nx.DiGraph()
    tgtrue.add_nodes_from(nodes)
    for i in range(three_col_format.shape[0]):
        c = "V"+str(int(three_col_format[i, 0]))
        e = "V"+str(int(three_col_format[i, 1]))
        tgtrue.add_edges_from([(c, e)])
        tgtrue.edges[c, e]['time'] = [int(three_col_format[i, 2])]

    gtrue, ogtrue, sgtrue = tgraph_to_graph(tgtrue)
    return gtrue, ogtrue, sgtrue




X = pd.read_csv('data/timeseries2.csv')

model = lingam.VARLiNGAM(lags=5)
model.fit(X)
model.causal_order_
print(model.causal_order_)

summary_matrix = np.sum(np.abs(model.adjacency_matrices_), axis=0)
# summary_matrix[summary_matrix != 0] = 1
# print(summary_matrix)

nodes = string_nodes(X.columns)

three_col_format_ground_truth = np.loadtxt('data/sim2_gt_processed.csv', delimiter=',')
gtrue, ogtrue, sgtrue = three_col_format_to_graphs(nodes, three_col_format_ground_truth)

other_matrix = summary_matrix.copy()
np.fill_diagonal(other_matrix, 0)

ghat = nx.from_numpy_array(summary_matrix.T, create_using=nx.DiGraph)
for u, v, d in ghat.edges(data=True):
    del d['weight']
mapping = {i: f'V{i}' for i in ghat.nodes()}
ghat = nx.relabel_nodes(ghat, mapping)

oghat = nx.from_numpy_array(other_matrix.T, create_using=nx.DiGraph)
for u, v, d in oghat.edges(data=True):
    del d['weight']
mapping = {i: f'V{i}' for i in oghat.nodes()}
oghat = nx.relabel_nodes(oghat, mapping)

from evaluation import GraphComparison
gc = GraphComparison(ghat, oghat)

# total
precision_a = gc._precision(gtrue, "all_adjacent")
recall_a = gc._recall(gtrue, "all_adjacent")
fscore_a = gc._f1(gtrue, "all_adjacent")
precision_o = gc._precision(gtrue, "all_oriented")
recall_o = gc._recall(gtrue, "all_oriented")
fscore_o = gc._f1(gtrue, "all_oriented")
# print(precision_a)
# print(recall_a)
# print(fscore_a)
# print(precision_o)
# print(recall_o)
# print(fscore_o)

# other
precision_a_other = gc._precision(ogtrue, "all_adjacent")
recall_a_other = gc._recall(ogtrue, "all_adjacent")
fscore_a_other = gc._f1(ogtrue, "all_adjacent")
precision_o_other = gc._precision(ogtrue, "all_oriented")
recall_o_other = gc._recall(ogtrue, "all_oriented")
fscore_o_other = gc._f1(ogtrue, "all_oriented")
# print(precision_a_other)
# print(recall_a_other)
# print(fscore_a_other)
# print(precision_o_other)
# print(recall_o_other)
# print(fscore_o_other)



# import matplotlib.pyplot as plt
# plt.figure(figsize=(8, 6))
# pos = nx.spring_layout(estimated_summary)
# nx.draw(estimated_summary, pos, with_labels=True, node_size=700, node_color='lightblue', font_size=12, font_color='black', edge_color='gray', arrows=True)
# edge_labels = nx.get_edge_attributes(estimated_summary, 'weight')
# nx.draw_networkx_edge_labels(estimated_summary, pos, edge_labels=edge_labels)
# plt.title("Estimated Summary Graph")
# plt.show()

# plt.figure(figsize=(8, 6))
# pos = nx.spring_layout(gtrue)
# nx.draw(gtrue, pos, with_labels=True, node_size=700, node_color='lightblue', font_size=12, font_color='black', edge_color='gray', arrows=True)
# edge_labels = nx.get_edge_attributes(gtrue, 'weight')
# nx.draw_networkx_edge_labels(gtrue, pos, edge_labels=edge_labels)
# plt.title("True Graph")
# plt.show()