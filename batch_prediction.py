import networkx as nx
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_single(data, lag, G, stock_index, train_frac=0.8):
    predicted = []
    causes_index = list(G.predecessors(stock_index))
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

def calculate_cumulative_portfolio_returns(data, predictions, winner_frac):
    data_backtest = data[-(predictions.shape[0]+1):]
    predicted_returns = (predictions - data_backtest[:-1]) / data_backtest[:-1]
    real_returns = (data_backtest[1:] - data_backtest[:-1]) / data_backtest[:-1]
    num_stocks = data.shape[1]
    num_winners = int(num_stocks * winner_frac)
    portfolio_returns = []
    winners = np.argpartition(predicted_returns, -num_winners, axis=1)[:, -num_winners:]
    losers = np.argpartition(predicted_returns, num_winners, axis=1)[:, :num_winners]

    for i in range(predictions.shape[0]):
        winner_return = np.mean(real_returns[i, winners[i]])
        loser_return = np.mean(real_returns[i, losers[i]])
        portfolio_return = winner_return - loser_return
        portfolio_returns.append(portfolio_return)
        
    return np.exp(np.sum(np.log(np.array(portfolio_returns)+1)))-1

# predict
G = nx.convert_node_labels_to_integers(nx.read_adjlist('./causal_graph/sp500_graph_varlingam_lag_3.txt', create_using=nx.DiGraph))
data = pd.read_csv('./data/Cleaned_S_P_500_Data.csv', delimiter=',', index_col=False, header=0)
column_names = data.columns.tolist()
data = data.to_numpy()
predictions = predict_batch(data, 3, G)
np.savetxt("./predictions/sp500_predictions_varlingam_lag_3.csv", predictions, delimiter=",", header=",".join(column_names), comments='')

# backtest
import matplotlib.pyplot as plt

frac = np.arange(0.01, 0.5, step=0.01)
cpr = [calculate_cumulative_portfolio_returns(data, predictions, f) for f in frac]

plt.plot(frac, cpr)