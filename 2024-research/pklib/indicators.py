import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from pkindicators import calculate_zigzag

def create_comparison_features(df, column_groups):
    """
    This function takes a DataFrame and an array of tuples of column names (with each tuple containing 
    two or more column names), and returns a new DataFrame containing boolean features that compare 
    all possible pairs of columns in each tuple.
    
    Parameters:
    df (pd.DataFrame): Original DataFrame
    column_groups (list): List of tuples, where each tuple contains two or more column names to compare
    
    Returns:
    pd.DataFrame: A new DataFrame containing the comparison features for all pairs of columns
    """
    new_features = pd.DataFrame()

    # Iterate over the array of column name tuples
    for group in column_groups:
        # Create pairwise comparisons within each tuple (group)
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                col1 = group[i]
                col2 = group[j]
                # Create boolean column for the comparison (col1 > col2)
                new_features[f'{col1}_gt_{col2}'] = df[col1] > df[col2]

    return new_features

def create_moving_average_features(df, ema_periods, sma_periods, column='close'):
    """
    This function takes a DataFrame and two separate lists of periods for EMAs and SMAs, and returns a new DataFrame 
    containing both Exponential Moving Averages (EMAs) and Simple Moving Averages (SMAs) for the specified periods.
    
    Parameters:
    df (pd.DataFrame): Original DataFrame with at least one column (e.g., 'close') used for EMA and SMA calculation.
    ema_periods (list): List of periods for which to calculate EMAs (e.g., [10, 20, 50]).
    sma_periods (list): List of periods for which to calculate SMAs (e.g., [10, 20, 50]).
    column (str): The name of the column in the DataFrame to use for calculating EMAs and SMAs (default is 'close').
    
    Returns:
    pd.DataFrame: A new DataFrame containing both EMA and SMA features for each period with the same index as the input DataFrame.
    """
    # Initialize a DataFrame to store the moving average features
    ma_features = pd.DataFrame(index=df.index)
    
    # Calculate EMA for each period and add to the new DataFrame
    for period in ema_periods:
        ma_features[f'ema_{period}'] = df[column].ewm(span=period, adjust=False).mean()
    
    # Calculate SMA for each period and add to the new DataFrame
    for period in sma_periods:
        ma_features[f'sma_{period}'] = df[column].rolling(window=period, min_periods=1).mean()
    
    return ma_features


def create_signed_difference_features_multi(df, column_threshold_pairs):
    """
    Create a new DataFrame with features indicating whether the signed percentage difference 
    between pairs of columns is below each threshold, for each tuple in the passed array.
    
    Parameters:
    df (pd.DataFrame): The original DataFrame with multiple columns.
    column_threshold_pairs (list): List of tuples, where each tuple contains:
                                   - (col1, col2, thresholds), with col1 and col2 being column names,
                                     and thresholds being a list of thresholds for those columns.
    
    Returns:
    pd.DataFrame: A new DataFrame with binary features indicating whether the signed percentage 
                  difference between column pairs is below the specified thresholds.
    """
    # Initialize a new DataFrame to store the features
    feature_df = pd.DataFrame(index=df.index)
    
    # Loop through each tuple (col1, col2, thresholds)
    for col1, col2, thresholds in column_threshold_pairs:
        # Calculate the signed percentage difference between col1 and col2
        signed_percentage_diff = ((df[col2] - df[col1]) / df[col1]) * 100
        
        # Create features for each threshold in the thresholds list
        for threshold in thresholds:
            feature_name = f'{col1}_vs_{col2}_below_{threshold}'
            feature_df[feature_name] = (signed_percentage_diff < threshold).astype(int)
    
    return feature_df


def add_bollinger_bands(df, periods, multiplier=2):
    """
    Add Bollinger Bands to the DataFrame for multiple periods.

    Args:
    - df: DataFrame containing 'Close' prices.
    - periods: List of periods for which to calculate Bollinger Bands.
    - multiplier: Multiplier for the standard deviation (default is 2).
    
    Returns:
    - df: DataFrame with Bollinger Bands added for each period.
    """
    
    # Function to calculate Bollinger Bands for a specific period
    def calculate_bollinger_bands(df, period, multiplier=2):
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        dch_up = df['close'].rolling(window=period).max()
        dch_dn = df['close'].rolling(window=period).min()
        upper_band = sma + (std * multiplier)
        lower_band = sma - (std * multiplier)
        return sma, upper_band, lower_band, std, dch_up, dch_dn

    # Iterate over the list of periods and calculate Bollinger Bands
    for period in periods:
        sma, upper_band, lower_band, std, dch_up, dch_dn = calculate_bollinger_bands(df, period, multiplier)
        # Add the results to the DataFrame
        df[f'BB_{period}_SMA'] = sma
        df[f'BB_{period}_STD'] = std
        df[f'BB_{period}_Upper'] = upper_band
        df[f'BB_{period}_Lower'] = lower_band
        df[f'BB_{period}_DchUp'] = dch_up
        df[f'BB_{period}_DchDn'] = dch_dn

    return df

epsilon = 0.2

# fib_levels = np.array([-1.0, -0.786, -0.618, -0.5, -0.382, -0.236, 0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.236, 1.5, 1.618, 1.786, 2.0, 2.236, 2.382, 2.5, 2.628, 2.786, 3, 3.382, 3.618, 4, 5])
fib_levels = np.array([-1.0, -0.618, -0.236, 0.0, 0.236, 0.5, 0.618, 0.786, 1.0, 1.236, 1.618, 2.0, 2.5, 3, 4, 5])

fib_columns = [f'fib({fib})' for fib in fib_levels]
# fib_columns 

def calculate_fib_levels(highs, lows, directions, fib_levels=fib_levels):
    # Ensure highs, lows, and directions are numpy arrays
    highs = np.asarray(highs)
    lows = np.asarray(lows)
    directions = np.asarray(directions)

    # Flip highs and lows based on direction (-1 means flip)
    adjusted_highs = np.where(directions == 1, highs, lows)
    adjusted_lows = np.where(directions == 1, lows, highs)

    # Calculate the difference between adjusted high and low
    diff = adjusted_highs - adjusted_lows

    # Calculate the Fibonacci levels by applying the levels to the differences
    fib_matrix = np.outer(diff, fib_levels)
    
    # Calculate the actual levels by adding them to the low (base) level
    fib_levels_array = adjusted_lows[:, np.newaxis] + fib_matrix

    return fib_levels_array


def get_fib_data(asset, quote, timeframe, exchange):
    # asset, quote, timeframe, exchange = 'BTC', 'USDT', '8h', 'binance'
    data = load_candles('binance',asset, quote, timeframe)#['2020':'2024']#.iloc[-35000:-5000]
        
    # Call the calculate_zigzag function from the C module
    high_low_markers, turning_points = calculate_zigzag(data['close'].values, epsilon=epsilon)

    # Store the results back into the DataFrame for easier plotting
    # data['HighLowMarkers'] = high_low_markers
    # data['TurningPoints'] = turning_points

    # Get the indices of highs and lows
    # highs_idx = data.index[data['HighLowMarkers'] == 1]
    # lows_idx = data.index[data['HighLowMarkers'] == -1]
    highs_idx = data.index[high_low_markers == 1]
    lows_idx = data.index[turning_points == -1]

    running_highs = (np.where(high_low_markers == 1, 1, np.nan) * data['close']).ffill()
    running_lows = (np.where(high_low_markers == -1, 1, np.nan) * data['close']).ffill()


    running_highs_idx = pd.Series(np.where(high_low_markers == 1, 1, np.nan) * np.arange(len(data))).set_axis(data.index).ffill()
    running_lows_idx = pd.Series(np.where(high_low_markers == -1, 1, np.nan) * np.arange(len(data))).set_axis(data.index).ffill()

    # Combine the indices and sort them
    turning_points_idx = sorted(highs_idx.union(lows_idx))

    # Assuming calculate_fib_levels is defined elsewhere in your code
    fibs = calculate_fib_levels(running_lows, running_highs, ((running_highs_idx > running_lows_idx) * 2 - 1))

    df_fibs = data.join(pd.DataFrame(fibs, columns=fib_columns, index=data.index))
    return df_fibs.dropna()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def donchian(data, period):
    """Calculates Donchian channel average."""
    return (data['low'].rolling(window=period).min() + data['high'].rolling(window=period).max()) / 2

def ichimoku_cloud_indicator(df, conversion_periods=9, base_periods=26, lagging_span2_periods=52, displacement=26):
    """Calculates Ichimoku Cloud lines and returns as a DataFrame."""
    
    # Conversion Line (Tenkan-sen)
    conversion_line = donchian(df, conversion_periods)
    
    # Base Line (Kijun-sen)
    base_line = donchian(df, base_periods)
    
    # Leading Span A (Senkou Span A)
    lead_line1 = (conversion_line + base_line) / 2
    
    # Leading Span B (Senkou Span B)
    lead_line2 = donchian(df, lagging_span2_periods)
    
    # Lagging Span (Chikou Span)
    lagging_span = df['close'].shift(-displacement + 1)
    
    # Shifted Lead Lines
    lead_line1_shifted = lead_line1.shift(displacement - 1)
    lead_line2_shifted = lead_line2.shift(displacement - 1)
    
    # Kumo Cloud Upper and Lower lines
    kumo_upper = np.where(lead_line1_shifted > lead_line2_shifted, lead_line1_shifted, lead_line2_shifted)
    kumo_lower = np.where(lead_line1_shifted < lead_line2_shifted, lead_line1_shifted, lead_line2_shifted)
    
    # Return the indicator lines as a DataFrame
    return pd.DataFrame({
        'tenkan': conversion_line,
        'kijun': base_line,
        # 'Lagging Span': lagging_span,
        'lead_span_A': lead_line1_shifted,
        'lead_span_B': lead_line2_shifted,
        'kumo_upper': kumo_upper,
        'kumo_lower': kumo_lower
    }, index=df.index)

def plot_ichimoku_cloud(df, ichimoku_data):
    """Plots the Ichimoku Cloud using the calculated lines."""
    
    plt.figure(figsize=(20, 6))
    
    # Plot Conversion Line (Tenkan-sen)
    plt.plot(df.index, df['close'], label='Close price', color='#7992FF', lw=0.5)
    
    # Plot Conversion Line (Tenkan-sen)
    plt.plot(df.index, ichimoku_data['tenkan'], label='Conversion Line (Tenkan-sen)', color='#2962FF', lw=0.5)
    
    # Plot Base Line (Kijun-sen)
    plt.plot(df.index, ichimoku_data['kijun'], label='Base Line (Kijun-sen)', color='#B71C1C', lw=0.5)
    
    # # Plot Lagging Span (Chikou Span)
    # plt.plot(df.index, ichimoku_data['Lagging Span'], label='Lagging Span (Chikou Span)', color='#43A047')
    
    # # Plot Leading Span A (Senkou Span A)
    # plt.plot(df.index, ichimoku_data['Leading Span A'], label='Leading Span A (Senkou Span A)', color='#A5D6A7')
    
    # # Plot Leading Span B (Senkou Span B)
    # plt.plot(df.index, ichimoku_data['Leading Span B'], label='Leading Span B (Senkou Span B)', color='#EF9A9A')
    
    # Plot Kumo Cloud Upper and Lower lines
    plt.fill_between(df.index, ichimoku_data['kumo_upper'], ichimoku_data['kumo_lower'], 
                     where=ichimoku_data['kumo_upper'] > ichimoku_data['kumo_lower'], facecolor='green', alpha=0.3)
    plt.fill_between(df.index, ichimoku_data['kumo_upper'], ichimoku_data['kumo_lower'], 
                     where=ichimoku_data['kumo_upper'] <= ichimoku_data['kumo_lower'], facecolor='red', alpha=0.3)
    
    # Set titles and labels
    plt.title('Ichimoku Cloud')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend(loc='best')
    plt.grid()
    plt.show()

