import time
import numpy as np
import pandas as pd
import networkx as nx
import graphviz
import lingam
from lingam.utils import make_dot, print_causal_directions, print_dagc
from evaluation import GraphComparison
from os import listdir
from os.path import isfile, join
import statistics

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

def three_col_format_to_graphs(nodes, three_col_format):
    tgtrue = nx.DiGraph()
    tgtrue.add_nodes_from(nodes)
    for i in range(three_col_format.shape[0]):
        c = "V"+str(int(three_col_format[i, 0]))
        e = "V"+str(int(three_col_format[i, 1]))
        tgtrue.add_edges_from([(c, e)])
        tgtrue.edges[c, e]['time'] = [int(three_col_format[i, 2])]

    gtrue, ogtrue = tgraph_to_graph(tgtrue)
    return gtrue, ogtrue

def run_on_data(files_input_name):
    results = {'precision_a': [], 'recall_a': [], 'fscore_a': [], 'precision_o': [], 'recall_o': [], 'fscore_o': [], 'precision_a_other': [], 'recall_a_other': [], 'fscore_a_other': [], 'precision_o_other': [], 'recall_o_other': [], 'fscore_o_other': []}

    for i in range(len(files_input_name)):
        file_input_name = files_input_name[i]
        data = pd.read_csv('./data/selected/' + file_input_name, delimiter=',', index_col=False, header=0)
        nodes = string_nodes(data.columns)

        idx_ground_truth_file = file_input_name.split('timeseries')[1].split('.csv')[0]
        file_ground_truth_name = "sim"+idx_ground_truth_file+"_gt_processed"
        three_col_format_ground_truth = np.loadtxt('./data/ground_truth/' + file_ground_truth_name + '.csv',
                                                delimiter=',')
        gtrue, ogtrue = three_col_format_to_graphs(nodes, three_col_format_ground_truth)

        model = lingam.VARLiNGAM(lags=5)
        model.fit(data)
        summary_matrix = np.sum(np.abs(model.adjacency_matrices_), axis=0)
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

        gc = GraphComparison(ghat, oghat)

        # total
        precision_a = gc._precision(gtrue, "all_adjacent")
        recall_a = gc._recall(gtrue, "all_adjacent")
        fscore_a = gc._f1(gtrue, "all_adjacent")
        precision_o = gc._precision(gtrue, "all_oriented")
        recall_o = gc._recall(gtrue, "all_oriented")
        fscore_o = gc._f1(gtrue, "all_oriented")

        # other
        precision_a_other = gc._precision(ogtrue, "all_adjacent")
        recall_a_other = gc._recall(ogtrue, "all_adjacent")
        fscore_a_other = gc._f1(ogtrue, "all_adjacent")
        precision_o_other = gc._precision(ogtrue, "all_oriented")
        recall_o_other = gc._recall(ogtrue, "all_oriented")
        fscore_o_other = gc._f1(ogtrue, "all_oriented")

        results['precision_a'].append(precision_a)
        results['recall_a'].append(recall_a)
        results['fscore_a'].append(fscore_a)
        results['precision_o'].append(precision_o)
        results['recall_o'].append(recall_o)
        results['fscore_o'].append(fscore_o)
        results['precision_a_other'].append(precision_a_other)
        results['recall_a_other'].append(recall_a_other)
        results['fscore_a_other'].append(fscore_a_other)
        results['precision_o_other'].append(precision_o_other)
        results['recall_o_other'].append(recall_o_other)
        results['fscore_o_other'].append(fscore_o_other)

    return results

path_input = './data/selected/'
files_input_name = [f for f in listdir(path_input) if isfile(join(path_input, f)) and not f.startswith('.')]
results_dict = run_on_data(files_input_name)

final_results_dict = {
    'precision_a': {'mean': 0, 'std_dev': 0},
    'recall_a': {'mean': 0, 'std_dev': 0},
    'fscore_a': {'mean': 0, 'std_dev': 0},
    'precision_o': {'mean': 0, 'std_dev': 0},
    'recall_o': {'mean': 0, 'std_dev': 0},
    'fscore_o': {'mean': 0, 'std_dev': 0},
    'precision_a_other': {'mean': 0, 'std_dev': 0},
    'recall_a_other': {'mean': 0, 'std_dev': 0},
    'fscore_a_other': {'mean': 0, 'std_dev': 0},
    'precision_o_other': {'mean': 0, 'std_dev': 0},
    'recall_o_other': {'mean': 0, 'std_dev': 0},
    'fscore_o_other': {'mean': 0, 'std_dev': 0}
}

for key, values in results_dict.items():
    mean_value = statistics.mean(values)
    std_dev_value = statistics.stdev(values)
    
    final_results_dict[key]['mean'] = mean_value
    final_results_dict[key]['std_dev'] = std_dev_value

for key, stats in final_results_dict.items():
    print(f"{key} - Mean: {stats['mean']:.2f}, Standard Deviation: {stats['std_dev']:.2f}")