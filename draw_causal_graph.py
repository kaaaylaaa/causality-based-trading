import networkx as nx
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
import os

def filter_causal_graph(summary_matrix, tickers, percent):
    G = nx.from_numpy_array(summary_matrix.T, create_using=nx.DiGraph)
    mapping = {i: tickers[i] for i in G.nodes()}
    G = nx.relabel_nodes(G, mapping)
    # delete all self-loops
    G_major = G.copy()
    self_loops = list(nx.selfloop_edges(G_major))
    G_major.remove_edges_from(self_loops)
    # filter edges by percentile
    percentile = np.percentile(summary_matrix, percent)
    for u, v, data in list(G_major.edges(data=True)):
        if data.get('weight', 0) < percentile:
            G_major.remove_edge(u, v)
    # delete isolated nodes
    isolated_nodes = [node for node in G_major.nodes() if G_major.degree(node) == 0]
    G_major.remove_nodes_from(isolated_nodes)
    return G_major

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print('Usage: summary_matrix_file data percent algorithm market lag')
        sys.exit()

    output_directory = "./plots"
    os.makedirs(output_directory, exist_ok=True)

    summary_matrix_file = sys.argv[1]
    data_file = sys.argv[2]
    percent = float(sys.argv[3])
    algorithm = sys.argv[4]
    market = sys.argv[5]
    lag = int(sys.argv[6])

    summary_matrix = np.genfromtxt(summary_matrix_file, delimiter=',', dtype=None, encoding=None)
    tickers = pd.read_csv(data_file, delimiter=',', nrows=1).columns.to_list()

    plot_filename = os.path.join(output_directory, f'{market}_major_causal_graph_{algorithm}_lag_{lag}.pdf')
    G_major = filter_causal_graph(summary_matrix, tickers, percent)
    pos = nx.spring_layout(G_major, seed=42, k=0.5, iterations=100)
    plt.figure(figsize=(10, 8))
    degree_dict = {node: G_major.degree(node) for node in G_major.nodes()}
    node_sizes = [degree_dict[node] * 100 for node in G_major.nodes()]
    nx.draw(G_major, pos, with_labels=True, node_size=node_sizes, node_color='skyblue', font_size=7, font_color='black', edge_color='gray', arrows=True, arrowsize=7)
    plt.savefig(plot_filename)

    in_degrees = dict(G_major.in_degree())
    stocks_with_most_causes = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    top_cause_filename = os.path.join(output_directory, f'{market}_stocks_with_most_causes_{algorithm}_lag_{lag}.txt')
    with open(top_cause_filename, "w") as f:
        f.write("Top 10 stocks with the most causes:\n")
        for node, degree in stocks_with_most_causes:
            sorted_causes = sorted(G_major.predecessors(node), key=lambda pred: G_major[pred][node]['weight'], reverse=True)
            f.write(f"Node {node}: {degree} causes {sorted_causes}\n")

    out_degrees = dict(G_major.out_degree())
    stocks_with_most_effects = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    top_effect_filename = os.path.join(output_directory, f'{market}_stocks_with_most_effects_{algorithm}_lag_{lag}.txt')
    with open(top_effect_filename, "w") as f:
        f.write("Top 10 stocks with the most effects:\n")
        for node, degree in stocks_with_most_effects:
            sorted_effects = sorted(G_major.successors(node), key=lambda succ: G_major[node][succ]['weight'], reverse=True)
            f.write(f"Node {node}: {degree} effects {sorted_effects}\n")

    total_degrees = dict(G_major.degree())
    stocks_with_most_connections = sorted(total_degrees.items(), key=lambda x: x[1], reverse=True)[:20]
    top_connection_filename = os.path.join(output_directory, f'{market}_stocks_with_most_connections_{algorithm}_lag_{lag}.txt')
    with open(top_connection_filename, "w") as f:
        f.write("Top 20 stocks with the most connections:\n")
        for node, degree in stocks_with_most_connections:
            sorted_causes = sorted(G_major.predecessors(node), key=lambda pred: G_major[pred][node]['weight'], reverse=True)
            sorted_effects = sorted(G_major.successors(node), key=lambda succ: G_major[node][succ]['weight'], reverse=True)
            f.write(f"Node {node}: {degree} connections, {G_major.in_degree(node)} causes {sorted_causes}, {G_major.out_degree(node)} effects {sorted_effects}\n")
