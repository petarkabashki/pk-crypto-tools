#%%

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import pandas_ta as ta
import math
# from tqdm import tqdm
# import gc
# import time
import json
from pprint import pprint
# import pandas_ta
# import talib
import pickle
# from position_tools import calculate_trades, calculate_positions, count_since_last_signal

# from pklibs import *

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import talib

# from pklib.strategy import *
from pklib.utilities import *
# from pklib.pkindicators import calculate_zigzag
from pklib.indicators import *

# from sklearn.metrics import confusion_matrix
# from sklearn.metrics import confusion_matrix
# from sklearn.metrics import precision_score, recall_score

# import seaborn as sns
# from pklib.rl import *

### IMPORTANT
# pip install numpy==1.26.4 pandas==2.2.1 --force-reinstall
#%%
import dotenv
import os

# Reload the variables in your '.env' file (override the existing variables)
dotenv.load_dotenv(".env", override=True)

# 'MY_VAR' is refreshed now
print('HIP_VISIBLE_DEVICES = ', os.environ.get('HIP_VISIBLE_DEVICES')) # MY_VAR = HELLO_BOB
#%%
import torch
import torch as T
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from sklearn.metrics import precision_recall_fscore_support

# Add this near the top of your script, after importing torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

#%%

def get_signal(df, lookback_period, target_period, min_target_pct, risk_2_reward, max_capital, lookback_column='low'):
    fwd_min = df.low.rolling(target_period).min().shift(-target_period)
    fwd_max = df.high.rolling(target_period).max().shift(-target_period)
    fwd_rwd_pct = (fwd_max / df.close) - 1    
    stoploss = df[lookback_column].rolling(lookback_period).min() 
    
    risk_pct = df.close / stoploss - 1
    target_pct = risk_pct * risk_2_reward
    target = df.close * (1 + target_pct)
    
    # Calculate the required capital for each trade
    required_capital = df.close * (1 / risk_pct)
    
    Y = (fwd_min > stoploss)
    Y = Y & (fwd_rwd_pct > target_pct)
    Y = Y & (target_pct > min_target_pct)
    # Y = Y & (required_capital <= max_capital)  # New condition
    Y = Y.fillna(False)
    
    return Y, (stoploss, target), (risk_pct, target_pct, required_capital)

#%%

# # Declare parameters for get_signal
# lookback_period = 14
# target_period = 20
# min_target_pct = 0.02
# risk_2_reward = 2
# max_capital = 10000  # Assuming a maximum capital of $10,000 per trade
# lookback_column = 'low'
# df = df_ohlcv

# # Call get_signal function
# Y, (stoploss, target), (risk_pct, target_pct, required_capital) = get_signal(
#     df, 
#     lookback_period, 
#     target_period, 
#     min_target_pct, 
#     risk_2_reward, 
#     max_capital, 
#     lookback_column
# )

# # Print or process the results as needed
# print("Signal generated:")
# print(f"Number of positive signals: {Y.sum()}")
# print(f"Average risk percentage: {risk_pct.mean():.2%}")
# print(f"Average target percentage: {target_pct.mean():.2%}")
# print(f"Average required capital: ${required_capital.mean():.2f}")

#%%

def add_lagged(df, feature_list, lag_periods):
    df_lagged = df#.copy()
    
    # For each feature, create lagged features
    for feature in feature_list:
        for lag in lag_periods:
            lagged_feature_name = f'{feature}_{lag}'.replace('-', '__')
            df_lagged[lagged_feature_name] = df[feature].shift(lag)
    
    return df_lagged
#%%
import pandas as pd
import numpy as np
import talib

def calculate_talib_indicator(data, indicator_name, params_list, price_column='close'):
    """
    Calculate a TA-Lib indicator for multiple periods or parameters.

    Parameters:
    - data: pandas DataFrame containing price data.
    - indicator_name: string, name of the TA-Lib indicator function as a string.
    - params_list: list of dictionaries, each containing parameters for the indicator.
    - price_column: string, the column name in 'data' to use for price (default is 'close').

    Returns:
    - result_df: pandas DataFrame with indicator values for each set of parameters.
    """
    # Initialize an empty DataFrame to store results
    result_df = pd.DataFrame(index=data.index)

    # Get the indicator function from TA-Lib
    indicator_func = getattr(talib, indicator_name)

    for params in params_list:
        # Extract parameters
        params_copy = params.copy()  # Copy to avoid modifying the original
        suffix = '_'.join(f"{k}{v}" for k, v in params.items())

        # Prepare input data based on the indicator's requirements
        # Assuming most indicators use the 'close' price, adjust as needed
        input_data = data[price_column]

        # Calculate the indicator
        result = indicator_func(input_data, **params_copy)

        # If the result is a tuple (some indicators return multiple outputs), handle it
        if isinstance(result, tuple):
            for idx, res in enumerate(result):
                result_df[f"{indicator_name}_{suffix}_{idx}"] = res
        else:
            result_df[f"{indicator_name}_{suffix}"] = result

    return result_df

# Load your data
from pklib.utilities import load_candles

exchange = 'binance'
asset = 'BTC'
quote = 'USDT'
timeframe = '8h'
df = load_candles(exchange, asset, quote, timeframe)

# Define periods for moving averages and standard deviation
periods = [3, 5, 7, 10, 14, 17, 21, 26, 50, 80, 100, 200]

# Calculate indicators
indicators = {
    'SMA': calculate_talib_indicator(df, 'SMA', [{'timeperiod': p} for p in periods]),
    'EMA': calculate_talib_indicator(df, 'EMA', [{'timeperiod': p} for p in periods]),
    'STDDEV': calculate_talib_indicator(df, 'STDDEV', [{'timeperiod': p, 'nbdev': 1} for p in periods])
}

# Combine all indicators with the original DataFrame
df_with_indicators = pd.concat([df] + list(indicators.values()), axis=1)

# Separate price-based and STDDEV columns
price_columns = [col for col in df_with_indicators.columns if 'STDDEV' not in col]
stddev_columns = [col for col in df_with_indicators.columns if 'STDDEV' in col]

df_price = df_with_indicators[price_columns]
df_stddev = df_with_indicators[stddev_columns]

# Normalize price-based columns
df_price_normalized = np.log(df_price).sub(np.log(df_price['open']), axis=0)

# Normalize STDDEV columns
df_stddev_normalized = np.log(df_stddev.div(df_price['open'], axis=0))

# Combine normalized DataFrames
df_all_normalized = pd.concat([df_price_normalized, df_stddev_normalized], axis=1)

lagged_columns = [col for col in df_all_normalized.columns if (col.startswith('SMA_') and col.endswith('0')) or (col.startswith('EMA_') and col.endswith('0')) or (col.startswith('STDDEV_') and col.endswith('0') ) or col in ['high', 'low', 'close']]    

df_all_normalized = add_lagged(df_all_normalized, lagged_columns, lag_periods=[1,2,3,4,5,6,7,8,9,10,21,30,50,80,120,200])

df_all_normalized = df_all_normalized.dropna()
df_ohlcv = df.loc[df_all_normalized.index,:]

# Print summary information
print("Combined normalized DataFrame:")
print(df_all_normalized.head())
print(df_all_normalized.info())

print("\nValue ranges in normalized DataFrame:")
print(f"Min: {df_all_normalized.min().min()}, Max: {df_all_normalized.max().max()}")

# Store the column names for later use
normalized_columns = df_all_normalized.columns
normalized_columns = normalized_columns.tolist()

#%%
# df_all_normalized['open'] = 1e-8
[col for col in normalized_columns if (col.startswith('SMA_') and col.endswith('0')) or (col.startswith('EMA_') and col.endswith('0')) or (col.startswith('STDDEV_') and col.endswith('0') ) or col in ['high', 'low', 'close']]
# df_ohlcv
#%%

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
import numpy as np
import seaborn as sns
# Define the LSTM model
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.2):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

# Use the existing get_signal function with sample parameters
# Pre-declare arguments for get_signal function
lookback_period = 3
holding_period = 3
threshold = 0.01
direction = 2
initial_capital = 10000
lookback_column = 'low'

# Call get_signal function with pre-declared arguments
y, _, _ = get_signal(df_ohlcv, lookback_period, holding_period, threshold, direction, initial_capital, lookback_column=lookback_column)

# Prepare the data
X = df_all_normalized.values
y = y.loc[df_all_normalized.index]

# Create sequences
sequence_length = 10  # You can adjust this
X_seq = []
y_seq = []

for i in range(len(X) - sequence_length):
    X_seq.append(X[i:i+sequence_length])
    y_seq.append(y[i+sequence_length])

X_seq = np.array(X_seq)
y_seq = np.array(y_seq)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.5, random_state=42)

# Convert to PyTorch tensors and move to the appropriate device
X_train = torch.FloatTensor(X_train).to(device)
y_train = torch.FloatTensor(y_train).to(device)
X_test = torch.FloatTensor(X_test).to(device)
y_test = torch.FloatTensor(y_test).to(device)

# Create DataLoader
train_data = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_data, batch_size=256, shuffle=False)

# Initialize the model and move it to the appropriate device
input_size = X_train.shape[2]
hidden_size = 64  # or 128
num_layers = 1  # or 3
output_size = 1

# Initialize the model, criterion, and optimizer
model = LSTMModel(input_size, hidden_size, num_layers, output_size).to(device)

#%
pos_weight = torch.tensor([(len(y_train) - y_train.sum()) / y_train.sum()]).to(device)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.Adam(model.parameters(), lr=0.0005)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5, factor=0.5)

# Training loop
num_epochs = 1000
train_losses = []
best_loss = float('inf')
patience = 20
counter = 0
best_model = None

for epoch in range(num_epochs):
    model.train()
    epoch_loss = 0.0
    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs.squeeze(), batch_y)
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1)
        
        optimizer.step()
        epoch_loss += loss.item()
    
    avg_loss = epoch_loss / len(train_loader)
    train_losses.append(avg_loss)
    
    # Learning rate scheduling
    scheduler.step(avg_loss)
    
    # Early stopping check
    if avg_loss < best_loss:
        best_loss = avg_loss
        counter = 0
        best_model = model.state_dict()
    else:
        counter += 1
        if counter >= patience:
            print(f'Early stopping at epoch {epoch+1}')
            break
    
    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.6f}')

# Load the best model
model.load_state_dict(best_model)

# Plot training loss
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(train_losses) + 1), train_losses)
plt.title('Training Loss Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.yscale('log')
plt.grid(True)
plt.show()

#%%

# Evaluation
model.eval()
with torch.no_grad():
    test_outputs = model(X_test)
    test_loss = criterion(test_outputs.squeeze(), y_test)
    print(f'Test Loss: {test_loss.item():.4f}')

    # Convert probabilities to binary predictions
    predictions = (torch.sigmoid(test_outputs.squeeze()) > 0.5).float()
    
    # Compute confusion matrix (move tensors to CPU for numpy operations)
    conf_matrix = confusion_matrix(y_test.cpu().numpy(), predictions.cpu().numpy())
    print("Confusion Matrix:")
    print(conf_matrix)

    # Calculate precision, recall, and F1-score
    precision = precision_score(y_test.cpu().numpy(), predictions.cpu().numpy())
    recall = recall_score(y_test.cpu().numpy(), predictions.cpu().numpy())
    f1 = f1_score(y_test.cpu().numpy(), predictions.cpu().numpy())

    # Print the metrics
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-score: {f1:.4f}")

    # Calculate overall accuracy
    accuracy = accuracy_score(y_test.cpu().numpy(), predictions.cpu().numpy())
    print(f'Overall Accuracy: {accuracy:.4f}')

    # Visualize the confusion matrix
    plt.figure(figsize=(6,4))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()

# Check class distribution
print("Class distribution:")
print(y_train.sum().item() / len(y_train))

# If imbalanced, consider using class weights
pos_weight = torch.tensor([(len(y_train) - y_train.sum()) / y_train.sum()]).to(device)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

# Calculate precision, recall, and F1-score with class weights
precision = precision_score(y_test.cpu().numpy(), predictions.cpu().numpy())
recall = recall_score(y_test.cpu().numpy(), predictions.cpu().numpy())
f1 = f1_score(y_test.cpu().numpy(), predictions.cpu().numpy())

# Print the metrics with class weights
print(f"Precision with class weights: {precision:.4f}")
print(f"Recall with class weights: {recall:.4f}")
print(f"F1-score with class weights: {f1:.4f}")

# Calculate overall accuracy with class weights
accuracy = accuracy_score(y_test.cpu().numpy(), predictions.cpu().numpy())
print(f'Overall Accuracy with class weights: {accuracy:.4f}')

# Visualize the confusion matrix with class weights
plt.figure(figsize=(6,4))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix with class weights')
plt.show()

# Output the device on which the model is running
device = next(model.parameters()).device
print(f"The model is running on: {device}")

#%%
y_test.sum(), y_train.sum()
#%%

#%%

#%%