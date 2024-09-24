import networkx as nx
import numpy as np
import os
import lingam
import sys
import pandas as pd
from causal_discovery_varlingam import causal_discovery_varlingam
from causal_discovery_pcmci import causal_discovery_pcmci


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: sp500_data latest_sp500_data csi300_data pelosi_data')
        exit()
        
    output_directory = "./all_results"
    os.makedirs(output_directory, exist_ok=True)

    sp500_data_filename = sys.argv[1]
    latest_sp500_data_filename = sys.argv[2]
    csi300_data_filename = sys.argv[3]
    pelosi_data_filename = sys.argv[4]

    # data = np.genfromtxt(data_filename, delimiter=',', skip_header=1)
    # print('Running', market_name, num_lags, algorithm)
    # G, summary_matrix = causal_discovery_varlingam(data, num_lags)
    # output_filename = os.path.join(output_directory, f'{market_name}_graph_{algorithm}_lag_{num_lags}.txt')
    # nx.write_adjlist(G, output_filename)
    # matrix_filename = os.path.join(output_directory, f'{market_name}_summary_matrix_{algorithm}_lag_{num_lags}.csv')
    # np.savetxt(matrix_filename, summary_matrix, delimiter=',')


