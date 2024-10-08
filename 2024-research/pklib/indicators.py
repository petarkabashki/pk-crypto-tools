import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import talib

def add_shifted_columns(df, periods, columns=None, suffix=""):
    df_res = df # pd.DataFrame(index=df.index)
    if columns is None:
        columns = df.columns.values
    # result_df = df.copy()  # Make a copy of the original DataFrame
    
    for period in periods:
        for col in columns:
            # Shift the column forward by the specified period
            shifted_col_name = f'{col}_shifted_{period}{suffix}'
            df_res[shifted_col_name] = df[col].shift(periods=period)
    
    return df_res


# epsilon = 0.2

# # fib_levels = np.array([-1.0, -0.786, -0.618, -0.5, -0.382, -0.236, 0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.236, 1.5, 1.618, 1.786, 2.0, 2.236, 2.382, 2.5, 2.628, 2.786, 3, 3.382, 3.618, 4, 5])
# fib_levels = np.array([-1.0, -0.618, -0.236, 0.0, 0.236, 0.5, 0.618, 0.786, 1.0, 1.236, 1.618, 2.0, 2.5, 3, 4, 5])

# fib_columns = [f'fib({fib})' for fib in fib_levels]
# # fib_columns 

# def calculate_fib_levels(highs, lows, directions, fib_levels=fib_levels):
#     # Ensure highs, lows, and directions are numpy arrays
#     highs = np.asarray(highs)
#     lows = np.asarray(lows)
#     directions = np.asarray(directions)

#     # Flip highs and lows based on direction (-1 means flip)
#     adjusted_highs = np.where(directions == 1, highs, lows)
#     adjusted_lows = np.where(directions == 1, lows, highs)

#     # Calculate the difference between adjusted high and low
#     diff = adjusted_highs - adjusted_lows

#     # Calculate the Fibonacci levels by applying the levels to the differences
#     fib_matrix = np.outer(diff, fib_levels)
    
#     # Calculate the actual levels by adding them to the low (base) level
#     fib_levels_array = adjusted_lows[:, np.newaxis] + fib_matrix

#     return fib_levels_array


# def get_fib_data(asset, quote, timeframe, exchange):
#     # asset, quote, timeframe, exchange = 'BTC', 'USDT', '8h', 'binance'
#     data = load_candles('binance',asset, quote, timeframe)#['2020':'2024']#.iloc[-35000:-5000]
        
#     # Call the calculate_zigzag function from the C module
#     high_low_markers, turning_points = calculate_zigzag(data['close'].values, epsilon=epsilon)

#     # Store the results back into the DataFrame for easier plotting
#     # data['HighLowMarkers'] = high_low_markers
#     # data['TurningPoints'] = turning_points

#     # Get the indices of highs and lows
#     # highs_idx = data.index[data['HighLowMarkers'] == 1]
#     # lows_idx = data.index[data['HighLowMarkers'] == -1]
#     highs_idx = data.index[high_low_markers == 1]
#     lows_idx = data.index[turning_points == -1]

#     running_highs = (np.where(high_low_markers == 1, 1, np.nan) * data['close']).ffill()
#     running_lows = (np.where(high_low_markers == -1, 1, np.nan) * data['close']).ffill()


#     running_highs_idx = pd.Series(np.where(high_low_markers == 1, 1, np.nan) * np.arange(len(data))).set_axis(data.index).ffill()
#     running_lows_idx = pd.Series(np.where(high_low_markers == -1, 1, np.nan) * np.arange(len(data))).set_axis(data.index).ffill()

#     # Combine the indices and sort them
#     turning_points_idx = sorted(highs_idx.union(lows_idx))

#     # Assuming calculate_fib_levels is defined elsewhere in your code
#     fibs = calculate_fib_levels(running_lows, running_highs, ((running_highs_idx > running_lows_idx) * 2 - 1))

#     df_fibs = data.join(pd.DataFrame(fibs, columns=fib_columns, index=data.index))
#     return df_fibs.dropna()


def donchian(data, period):
    """Calculates Donchian channel average."""
    return (data['low'].rolling(window=period).min() + data['high'].rolling(window=period).max()) / 2

def add_ichimoku_cloud_indicator(df, params):
    df = pd.DataFrame(index=df.index)
    default_params = {
        'conversion_periods': 9,
        'base_periods': 26,
        'lagging_span2_periods': 52,
        'displacement': 26
    }
    
    # If a params dictionary is provided, override the default values
    if params:
        ichimoku_params = {**default_params, **params}
    else:
        ichimoku_params = default_params
    
    # Extract parameters from the dictionary
    conversion_periods = ichimoku_params['conversion_periods']
    base_periods = ichimoku_params['base_periods']
    lagging_span2_periods = ichimoku_params['lagging_span2_periods']
    displacement = ichimoku_params['displacement']
    
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
    
    # Create a DataFrame with the indicator lines
    ichimoku_df = pd.DataFrame({
        'tenkan': conversion_line,
        'kijun': base_line,
        'lead_span_A': lead_line1_shifted,
        'lead_span_B': lead_line2_shifted,
        'kumo_upper': kumo_upper,
        'kumo_lower': kumo_lower
    }, index=df.index)
    
    # If multi_to_original is True, merge the new columns into the original DataFrame
    
    # Otherwise, return only the DataFrame with the indicators
    return ichimoku_df


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

