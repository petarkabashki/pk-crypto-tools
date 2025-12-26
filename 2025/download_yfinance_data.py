import yfinance as yf
import pandas as pd
import argparse
from datetime import datetime, timedelta
import os

def download_data(ticker, timeframe='1d', start_date=None, end_date=None, output_file=None):
    """
    Downloads asset price data from Yahoo Finance.

    Args:
        ticker (str): The ticker symbol (e.g., AAPL).
        timeframe (str): The timeframe for the data (e.g., '1d', '1h', '5m'). Defaults to '1d'.
        start_date (str, optional): The start date for the data (YYYY-MM-DD). Defaults to 1 year ago.
        end_date (str, optional): The end date for the data (YYYY-MM-DD). Defaults to today.
        output_file (str, optional): The path to save the downloaded data. Defaults to './data/{ticker}_data.csv'.
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if output_file is None:
        output_file = os.path.join('data', f"{ticker}_data.csv")

    # Create the data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    print(f"Downloading {ticker} data with timeframe '{timeframe}' from {start_date} to {end_date}...")

    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval=timeframe
    )

    if data.empty:
        print(f"No data found for {ticker} with the specified parameters.")
        return

    data.columns = [c[0].lower() for c in data.columns]
    data = data[['open','high','low','close','volume']]
    # convert index to unix timestamp milliseconds
    data.index = data.index.astype('int64') // 10**6
    data.to_csv(output_file, index_label='Date')
    print(f"Data saved to {output_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download asset price data from Yahoo Finance.')
    parser.add_argument('ticker', type=str, help='The ticker symbol (e.g., AAPL)')
    parser.add_argument('--timeframe', type=str, default='1d', help='The timeframe for the data (e.g., 1d, 1h, 5m). Defaults to 1d.')
    parser.add_argument('--start_date', type=str, help='The start date for the data (YYYY-MM-DD). Defaults to 1 year ago.')
    parser.add_argument('--end_date', type=str, help='The end date for the data (YYYY-MM-DD). Defaults to today.')
    parser.add_argument('--output_file', type=str, help=f'The path to save the downloaded data. Defaults to ./data/{{ticker}}_data.csv.')

    args = parser.parse_args()

    download_data(args.ticker, args.timeframe, args.start_date, args.end_date, args.output_file)
