import numpy as np
import sys
import os
import csv
import matplotlib.pyplot as plt
import pandas as pd

def calculate_annualized_portfolio_returns(data, predictions, num_winners, datatype):
    if datatype == 'price':
        data_backtest = data[-(predictions.shape[0]+1):]
        predicted_returns = (predictions - data_backtest[:-1]) / data_backtest[:-1]
        real_returns = (data_backtest[1:] - data_backtest[:-1]) / data_backtest[:-1]
    elif datatype == 'return':
        data_backtest = data[-(predictions.shape[0]):]
        predicted_returns = predictions
        real_returns = data_backtest
    else:
        raise ValueError("Invalid datatype. It must be either 'price' or 'return'.")
    
    # num_stocks = data.shape[1]
    # num_winners = int(num_stocks * winner_frac)
    portfolio_returns = []
    winners = np.argpartition(predicted_returns, -num_winners, axis=1)[:, -num_winners:]
    losers = np.argpartition(predicted_returns, num_winners, axis=1)[:, :num_winners]

    for i in range(predictions.shape[0]):
        winner_return = np.mean(real_returns[i, winners[i]])
        loser_return = np.mean(real_returns[i, losers[i]])
        portfolio_return = winner_return - loser_return - 0.001
        portfolio_returns.append(portfolio_return)  
    cumulative_portfolio_return = np.exp(np.sum(np.log(np.array(portfolio_returns)+1)))-1
    annualized_return = (1+cumulative_portfolio_return)**(252/predictions.shape[0])-1
    return annualized_return, winners, losers, portfolio_returns

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('Usage: data_file prediction_file num_lags market_name algorithm datatype')
        # print('Usage: data_file prediction_file num_lags market_name algorithm test_winner_num datatype')
        exit()
        
    output_directory = "./backtesting"
    os.makedirs(output_directory, exist_ok=True)

    data_filename = sys.argv[1]
    predictions_filename = sys.argv[2]
    num_lags = int(sys.argv[3])
    market_name = sys.argv[4]
    algorithm = sys.argv[5]
    # test_winner_num = int(sys.argv[6])
    # datatype = sys.argv[7]
    datatype = sys.argv[6]

    data = np.genfromtxt(data_filename, delimiter=',', skip_header=1)
    predictions = np.genfromtxt(predictions_filename, delimiter=',', skip_header=1)

    predictions_self_filename = predictions_filename.replace("_predictions_", "_predictions_self_")
    predictions_self = np.genfromtxt(predictions_self_filename, delimiter=',', skip_header=1)
    
    # backtest
    print('Backtesting', market_name, num_lags, algorithm)
    # frac = np.arange(0.01, 0.5, step=0.01)
    n_winners_range = np.arange(1, max(int(0.2*data.shape[1]), 5))
    # print(n_winners_range)
    ar = [calculate_annualized_portfolio_returns(data, predictions, f, datatype)[0] for f in n_winners_range]
    ar_self = [calculate_annualized_portfolio_returns(data, predictions_self, f, datatype)[0] for f in n_winners_range]
    backtest_output_filename = os.path.join(output_directory, f'{market_name}_backtest_returns_{algorithm}_lag_{num_lags}.csv')
    backtest_returns = np.column_stack((n_winners_range, ar, ar_self))
    with open(backtest_output_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['winner_num', 'ar', 'ar_self'])
        writer.writerows(backtest_returns)
    print('Backtest Returns Saved', market_name, num_lags, algorithm)

    # plt.plot(n_winners_range, ar, label="causal discovery", color="blue")
    # plt.plot(n_winners_range, ar_self, label="self cause only", color="red")
    # # plot_title = f'{market_name}_{algorithm}_lag_{num_lags}'
    # # plt.title(plot_title)
    # plt.xlabel("Number of Winners/Losers")
    # plt.ylabel("Annualized Portfolio Return")
    # backtest_plot_filename = os.path.join(output_directory, f'{market_name}_backtest_returns_plot_{algorithm}_lag_{num_lags}.png')
    # plt.savefig(backtest_plot_filename)
    # print('Backtest Returns Plot Saved', market_name, num_lags, algorithm)

    # winner_filename = os.path.join(output_directory, f'{market_name}_{test_winner_num}_winners_{algorithm}_lag_{num_lags}.csv')
    # loser_filename = os.path.join(output_directory, f'{market_name}_{test_winner_num}_losers_{algorithm}_lag_{num_lags}.csv')
    # daily_port_return_filename = os.path.join(output_directory, f'{market_name}_daily_portfolio_returns_{test_winner_num}_{algorithm}_lag_{num_lags}.csv')
    # _,winners,losers,daily_port_returns = calculate_annualized_portfolio_returns(data, predictions, test_winner_num, datatype)
    # tickers = pd.read_csv(data_filename, delimiter=',', nrows=1).columns.to_list()
    # def index_to_ticker(index):
    #     return tickers[index]
    # vectorized_func = np.vectorize(index_to_ticker)
    # winner_tickers = vectorized_func(winners)
    # loser_tickers = vectorized_func(losers)

    # with open(winner_filename, 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(winner_tickers)
    
    # with open(loser_filename, 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(loser_tickers)

    # with open(daily_port_return_filename, mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(daily_port_returns)
    # print('Winners and Losers Saved', market_name, num_lags, algorithm)