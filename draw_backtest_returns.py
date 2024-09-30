import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import os
import sys

if __name__ == '__main__':
    if len(sys.argv) < 7:
        print('Usage: prediction_file backtest_file date_file algorithm market lag ticker')
        sys.exit()

    output_directory = "./plots"
    os.makedirs(output_directory, exist_ok=True)

    prediction_file = sys.argv[1]
    backtest_file = sys.argv[2]
    date_file = sys.argv[3]
    algorithm = sys.argv[4]
    market = sys.argv[5]
    lag = int(sys.argv[6])
    ticker = sys.argv[7]

    dates = pd.read_csv(date_file, delimiter=',', index_col=False, header=0)
    predictions = pd.read_csv(prediction_file, delimiter=',', index_col=False, header=0)
    start_date = str(dates.iloc[-(len(predictions)+1), 0])
    end_date = str(dates.iloc[-1, 0])
    formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
    formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
    
    if market in ['sp500', 'latest_sp500', 'pelosi']:
        start_data = yf.download(ticker, start=formatted_start_date)
        baseline_start = start_data["Close"].iloc[0]
        end_data = yf.download(ticker, start=formatted_end_date)
        baseline_end = end_data["Close"].iloc[0]
    elif market == 'csi300':
        baseline_start = 3971.06
        baseline_end = 4096.58
    else:
        print(f"Unsupported market: {market}")

    baseline_return = (baseline_end - baseline_start) / baseline_start
    baseline_annualized_return = (1+baseline_return)**(252/predictions.shape[0])-1

    backtest_returns = pd.read_csv(backtest_file, delimiter=',', index_col=False, header=0)
    winner_num = backtest_returns.iloc[:,0].tolist()
    ar = backtest_returns.iloc[:,1].tolist()
    ar_self = backtest_returns.iloc[:,2].tolist()
    ar_baseline = [baseline_annualized_return]*len(winner_num)

    plot_filename = os.path.join(output_directory, f"{market}_portfolio_performance_{algorithm}_lag_{lag}.pdf")

    if market in ['sp500', 'latest_sp500']:
        plt.figure(figsize=(5,3))
        plt.plot(winner_num, ar, label = 'Causal discovery', color = 'orange')
        plt.plot(winner_num, ar_self, label = 'Self-cause only', color = 'navy')
        plt.plot(winner_num, ar_baseline, label = 'SP500 Index', color = 'red', linestyle=':')
        peak_index = np.argmax(ar)
        peak_x = int(winner_num[peak_index])
        peak_y = round(ar[peak_index],2)
        plt.axvline(x=peak_x, color='gray', linestyle='--', label=f'Peak return')
        # plt.text(peak_x, peak_y, f'({peak_x}, {peak_y})', fontsize=12, ha='left', va='baseline')
        plt.xlabel('Number of winners/losers')
        plt.ylabel('Annualized return')
        plt.xticks([x for x in winner_num if x % 10 == 0])
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(plot_filename)
    elif market == 'pelosi':
        plt.figure(figsize=(5,3))
        plt.plot(winner_num, ar, label = 'Causal discovery', color = 'orange')
        plt.plot(winner_num, ar_self, label = 'Self-cause only', color = 'navy')
        plt.plot(winner_num, ar_baseline, label = 'NANC ETF', color = 'red', linestyle=':')
        peak_index = np.argmax(ar)
        peak_x = int(winner_num[peak_index])
        peak_y = round(ar[peak_index],2)
        plt.axvline(x=peak_x, color='gray', linestyle='--', label=f'Peak return')
        # plt.text(peak_x, peak_y, f'({peak_x}, {peak_y})', fontsize=12, ha='left', va='baseline')
        plt.xlabel('Number of winners/losers')
        plt.ylabel('Annualized return')
        plt.xticks(winner_num)
        plt.legend()
        plt.tight_layout()
        plt.savefig(plot_filename)
    elif market == 'csi300':
        plt.figure(figsize=(5,3))
        plt.plot(winner_num, ar, label = 'Causal discovery', color = 'orange')
        plt.plot(winner_num, ar_self, label = 'Self-cause only', color = 'navy')
        plt.plot(winner_num, ar_baseline, label = 'CSI300 Index', color = 'red', linestyle=':')
        peak_index = np.argmax(ar)
        peak_x = int(winner_num[peak_index])
        peak_y = round(ar[peak_index],2)
        plt.axvline(x=peak_x, color='gray', linestyle='--', label=f'Peak return')
        # plt.text(peak_x, peak_y, f'({peak_x}, {peak_y})', fontsize=12, ha='left', va='baseline')
        plt.xlabel('Number of winners/losers')
        plt.ylabel('Annualized return')
        plt.xticks([x for x in winner_num if x % 3 == 0])
        plt.legend()
        plt.tight_layout()
        plt.savefig(plot_filename)
    else:
        print(f"Unsupported market: {market}")