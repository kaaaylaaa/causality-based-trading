import os
import pandas as pd

folder_path = 'historical_data'
csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]

merged_data = pd.DataFrame()

for file in csv_files:
    
    df = pd.read_csv(file, usecols=['Date', 'Close'])
    stock_name = os.path.basename(file).replace('_historical_data.csv', '')
    df.rename(columns={'Close': stock_name}, inplace=True)
    
    if merged_data.empty:
        merged_data = df
    else:
        merged_data = pd.merge(merged_data, df, on='Date', how='outer')

merged_data.sort_values('Date', inplace=True)

print(merged_data['Date'].isnull().sum())
# merged_data = merged_data.iloc[:, 1:]
merged_data.to_csv('data/merged_sp500_data.csv', index=False)