import yfinance as yf
import os
import numpy as np

# ticker_symbol = 'AAPL'

def extract_historical_data(ticker_symbol, output_directory):
    ticker = yf.Ticker(ticker_symbol)

    historical_data = ticker.history(start="2014-01-01", end="2024-08-24")
    
    file_path = os.path.join(output_directory, f"{ticker_symbol}_historical_data.csv")

    historical_data.to_csv(file_path)
    print(f"File saved: {ticker_symbol}")


if __name__ == '__main__':
    output_directory = "historical_data"
    os.makedirs(output_directory, exist_ok=True)
    constituents = np.genfromtxt('data/sp500_constituents.csv', delimiter=',', skip_header=1, usecols=0, dtype=str)
    for i in constituents:
        extract_historical_data(i.replace(".", "-"), output_directory=output_directory)
