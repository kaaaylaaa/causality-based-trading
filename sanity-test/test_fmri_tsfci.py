import time
import numpy as np
import pandas as pd
import networkx as nx
import graphviz
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

        tsfci_result_name = "result_"+idx_ground_truth_file
        tsfci_result_df = pd.read_csv('./tsfci_results/'+tsfci_result_name+'.csv', header=0, index_col=0)
        
        tsfci_dict = ts_fci_dataframe_to_dict(tsfci_result_df, nodes, nlags=5)
        tsfci_tgraph = dict_to_tgraph(nodes, tsfci_dict)
        ghat, oghat = tgraph_to_graph(tsfci_tgraph)

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