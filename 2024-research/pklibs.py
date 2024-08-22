import pandas as pd
import numpy as np


def load_json_candles(fname):
    data = pd.read_json(fname)
    data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data

def load_candles(exchange,base,quote,timeframe):
    fname = f'/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/{exchange}/{base}_{quote}-{timeframe}.json'
    return load_json_candles(fname)

def load_futures_candles(exchange,base,quote,timeframe):
    fname = f'/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/{exchange}/futures/{base}_{quote}_{quote}-{timeframe}-futures.json'
    return load_json_candles(fname)

def load_sp500_stock_candles(ticker):
    fname = f'/media/mu6mula/Data/Crypto-Data-Feed/sp500_data/{ticker}.csv'
    data = pd.read_csv(fname)
    data['Date'] = pd.to_datetime(data.Date)
    data.columns = [c.lower() for c in data.columns]
    data.set_index('date', inplace=True)
    return data

def load_russel2000_candles(ticker):
    fname = f'/media/mu6mula/Data/Crypto-Data-Feed/russell_2000_data/{ticker}.csv'
    data = pd.read_csv(fname)
    data['Date'] = pd.to_datetime(data.Date)
    data.columns = [c.lower() for c in data.columns]
    data.set_index('date', inplace=True)
    return data

def print_table(pairs, num_columns=4):
    # Calculate the maximum width for each column based on the titles and values
    max_width = max(len(title) for title, _ in pairs)
    
    # Increase the max_width if any value is longer than the titles
    max_value_width = max(len(str(value)) for _, value in pairs)
    max_width = max(max_width, max_value_width)

    # Create a format string for the columns
    column_format = "{:<" + str(max_width) + "} : {:>" + str(max_width) + "}"
    
    # Loop through the pairs and print them in a table format
    for i, (title, value) in enumerate(pairs):
        # Print a new line after every num_columns items
        if i % num_columns == 0 and i != 0:
            print()
        
        # Print the title-value pair with right alignment
        print(column_format.format(title, value), end="  ")

    # Print a final newline to ensure proper formatting
    print()