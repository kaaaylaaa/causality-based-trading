import networkx as nx
import numpy as np
import pandas as pd
import sys
import os
from sklearn.linear_model import LinearRegression

def predict_single(data, lag, G, stock_index, train_frac=0.8):
    predicted = []
    causes_name = list(G.predecessors(str(stock_index)))
    causes_index = [int(item) for item in causes_name]
    causes = data[:, causes_index]
    target = data[:, stock_index]
    Y = target[lag:]
    X = np.empty((0, lag*len(causes_index)))
    train_length = int(len(Y)*train_frac)
    
    for i in range(lag, data.shape[0]):
        lagged_vars = causes[(i-lag):i, :]
        long_vars = np.concatenate(lagged_vars)
        X = np.vstack([X, long_vars])
    
    for t in range(train_length, len(Y)):
        model = LinearRegression()
        model.fit(X[:t, :], Y[:t])
        prediction = model.predict(X[t, :].reshape(1, -1))
        predicted.append(prediction[0])
    return predicted

def predict_batch(data, lag, G, train_frac = 0.8):
    predictions = np.empty((0, 0))
    for i in range(data.shape[1]):
        print(f"Predicting stock {i}")
        predicted_list = predict_single(data, lag, G, i, train_frac)
        new_column = np.array(predicted_list).reshape(-1, 1)
        predictions = np.hstack((predictions, new_column)) if predictions.size else new_column
    return predictions



if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: data_file causal_graph num_lags market_name algorithm')
        exit()
        
    output_directory = "./predictions"
    os.makedirs(output_directory, exist_ok=True)

    data_filename = sys.argv[1]
    causal_graph_filename = sys.argv[2]
    num_lags = int(sys.argv[3])
    market_name = sys.argv[4]
    algorithm = sys.argv[5]
    

    data = pd.read_csv(data_filename, delimiter=',', index_col=False, header=0)
    G = nx.read_adjlist(causal_graph_filename, create_using=nx.DiGraph)
    column_names = data.columns.tolist()
    data = data.to_numpy()
    # predict
    print('Making Predictions', market_name, num_lags, algorithm)
    predictions = predict_batch(data, num_lags, G)
    predictions_output_filename = os.path.join(output_directory, f'{market_name}_predictions_{algorithm}_lag_{num_lags}.csv')
    np.savetxt(predictions_output_filename, predictions, delimiter=",", header=",".join(column_names), comments='')
    print('Predictions Saved', market_name, num_lags, algorithm)