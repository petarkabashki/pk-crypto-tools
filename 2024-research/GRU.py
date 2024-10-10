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

from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, accuracy_score
from tabulate import tabulate
import matplotlib.pyplot as plt

# Add this near the top of your script, after importing torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

#%%

def get_signal(df, lookback_period, target_period, min_target_pct, risk_2_reward):
    fwd_min = df.low.rolling(target_period).min().shift(-target_period)
    fwd_max = df.high.rolling(target_period).max().shift(-target_period)
    fwd_rwd_pct = (fwd_max / df.close) - 1    
    stoploss = df['low'].rolling(lookback_period).min()#.mul(0.995)
    
    risk_pct = df.close / stoploss - 1
    target_pct = risk_pct / risk_2_reward
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

#%%

# Load your data
from pklib.utilities import load_candles
def prepare_data(exchange, asset, quote, timeframe):
    # Load your data
    from pklib.utilities import load_candles

    df = load_candles(exchange, asset, quote, timeframe)

    # Define periods for moving averages and standard deviation
    periods = [3, 4, 5, 6, 7, 8, 9, 10, 14, 17, 21, 30, 50, 80, 100, 200]

    # Calculate indicators
    indicators = {
        'SMA': calculate_talib_indicator(df, 'SMA', [{'timeperiod': p} for p in periods]),
        'BBANDS': calculate_talib_indicator(df, 'BBANDS', [{'timeperiod': p, 'nbdevup': 2.5, 'nbdevdn': 2.5, 'matype': 0} for p in periods])
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

    df_all_normalized = add_lagged(df_all_normalized, lagged_columns, lag_periods=[1,2,3,4,5,6,7,8,9,14,16,21,26,30,40,50,100,200])

    df_all_normalized = df_all_normalized.dropna()
    df_ohlcv = df.loc[df_all_normalized.index,:]

    # Print summary information
    print("Combined normalized DataFrame:")
    print(df_all_normalized.head())
    print(df_all_normalized.info())

    print("\nValue ranges in normalized DataFrame:")
    print(f"Min: {df_all_normalized.min().min()}, Max: {df_all_normalized.max().max()}")

    # Store the column names for later use
    normalized_columns = df_all_normalized.columns.tolist()

    return df_all_normalized, df_ohlcv, normalized_columns

#%%
#%%

import torch
import torch.nn as nn
from torch.nn import functional as F
from torch.utils.data import TensorDataset, DataLoader
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.optim.lr_scheduler import LambdaLR
from sklearn.model_selection import train_test_split
import numpy as np
import seaborn as sns
# Define the GRU model
class GRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, fc_layers, output_size, dropout=0.5):
        super(GRUModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        
        # Batch normalization after GRU
        self.bn_gru = nn.BatchNorm1d(hidden_size)
        
        # Create fc layers based on the input array
        self.fc_layers = nn.ModuleList()
        self.bn_layers = nn.ModuleList()
        in_features = hidden_size
        for out_features in fc_layers:
            self.fc_layers.append(nn.Linear(in_features, out_features))
            self.bn_layers.append(nn.BatchNorm1d(out_features))
            in_features = out_features
        
        # Final output layer
        self.fc_out = nn.Linear(in_features, output_size)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.gru(x, h0)
        out = out[:, -1, :]  # Take the output from the last time step
        out = self.bn_gru(out)
        
        # Apply fc layers with batch normalization
        for fc, bn in zip(self.fc_layers, self.bn_layers):
            out = self.dropout(self.relu(bn(fc(out))))
        
        out = self.fc_out(out)
        return out
    
    def save_model(self, path):
        torch.save(self.state_dict(), path)
        print(f"Model saved to {path}")

    def load_model(self, path):
        self.load_state_dict(torch.load(path))
        print(f"Model loaded from {path}")

#%%
def train_gru_model(df_ohlcv, df_all_normalized, device, get_signal, signal_kw, num_epochs=100):


    # Call get_signal function with pre-declared arguments
    y, _, _ = get_signal(df_ohlcv, **signal_kw)

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
    X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.3, random_state=42)

    # Convert to PyTorch tensors and move to the appropriate device
    X_train = torch.FloatTensor(X_train).to(device)
    y_train = torch.FloatTensor(y_train).to(device)
    X_test = torch.FloatTensor(X_test).to(device)
    y_test = torch.FloatTensor(y_test).to(device)

    # Create DataLoader
    train_data = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_data, batch_size=512, shuffle=False)

    # Initialize the model and move it to the appropriate device
    input_size = X_train.shape[2]
    print(f'input_size: {input_size}')

    # Initialize the model, criterion, and optimizer
    hidden_size = 128*2
    fc_layers = [128]  
    model = GRUModel(input_size, hidden_size=hidden_size, num_layers=1, fc_layers=fc_layers, output_size=1, dropout=0.2).to(device)

    # Increase the weight for the positive class
    pos_weight = torch.tensor([(len(y_train) - y_train.sum()) / y_train.sum() * 2]).to(device)

    def focal_loss(pred, target, alpha=0.25, gamma=2):
        bce_loss = F.binary_cross_entropy_with_logits(pred, target, reduction='none')
        pt = torch.exp(-bce_loss)
        focal_loss = alpha * (1-pt)**gamma * bce_loss
        return focal_loss.mean()

    criterion = focal_loss
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-6)

    def warmup_lambda(epoch):
        if epoch < 50:
            return 0.1 * (epoch + 1)
        return 1.0128

    scheduler = LambdaLR(optimizer, lr_lambda=warmup_lambda)
    grad_norms = []

    accumulation_steps = 5  # Adjust as needed

    # Training loop
    
    train_losses = []
    best_loss = float('inf')
    patience = 70
    counter = 0
    best_model = None

    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0.0
        batch_grad_norms = []
        optimizer.zero_grad()  # Move this outside the batch loop
        
        for i, (batch_X, batch_y) in enumerate(train_loader):
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            loss = criterion(outputs.squeeze(), batch_y) / accumulation_steps
            loss.backward()
            
            # Track gradient norms
            total_norm = 0
            for p in model.parameters():
                if p.grad is not None:
                    param_norm = p.grad.data.norm(2)
                    total_norm += param_norm.item() ** 2
            total_norm = total_norm ** 0.5
            batch_grad_norms.append(total_norm)
            
            if (i + 1) % accumulation_steps == 0 or (i + 1) == len(train_loader):
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
                
                optimizer.step()
                optimizer.zero_grad()
            
            epoch_loss += loss.item() * accumulation_steps
        
        avg_loss = epoch_loss / len(train_loader)
        train_losses.append(avg_loss)
        grad_norms.append(np.mean(batch_grad_norms))
        
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
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.6f}, '
                  f'LR: {optimizer.param_groups[0]["lr"]:.2e}, '
                  f'Grad Norm: {grad_norms[-1]:.4f}')

    # Load the best model
    model.load_state_dict(best_model)

    # Plot training loss and gradient norms
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(range(1, len(train_losses) + 1), train_losses)
    plt.title('Training Loss Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.yscale('log')
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(range(1, len(grad_norms) + 1), grad_norms)
    plt.title('Gradient Norms Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Gradient Norm')
    plt.yscale('log')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    return model, (X_train, y_train), (X_test, y_test)


#%%
def evaluate_model(model, X_train, y_train, X_test, y_test, device):
    model.eval()
    with torch.no_grad():
        # Test data evaluation
        test_outputs = model(X_test)
        test_loss = nn.BCEWithLogitsLoss()(test_outputs.squeeze(), y_test)
        test_predictions = (torch.sigmoid(test_outputs.squeeze()) > 0.5).float()
        
        # Training data evaluation
        train_outputs = model(X_train)
        train_loss = nn.BCEWithLogitsLoss()(train_outputs.squeeze(), y_train)
        train_predictions = (torch.sigmoid(train_outputs.squeeze()) > 0.5).float()

        # Compute confusion matrices
        test_conf_matrix = confusion_matrix(y_test.cpu().numpy(), test_predictions.cpu().numpy())
        train_conf_matrix = confusion_matrix(y_train.cpu().numpy(), train_predictions.cpu().numpy())

        def print_conf_matrix(conf_matrix, title):
            print(f"{title} Confusion Matrix:")
            print(f"TN: {conf_matrix[0][0]}, FP: {conf_matrix[0][1]}")
            print(f"FN: {conf_matrix[1][0]}, TP: {conf_matrix[1][1]}")
            print()

        print_conf_matrix(test_conf_matrix, "Test")
        print(f'Train Loss: {train_loss.item():.4f}\n')
        print_conf_matrix(train_conf_matrix, "Train")

        # Calculate metrics for test data
        test_precision = precision_score(y_test.cpu().numpy(), test_predictions.cpu().numpy())
        test_recall = recall_score(y_test.cpu().numpy(), test_predictions.cpu().numpy())
        test_f1 = f1_score(y_test.cpu().numpy(), test_predictions.cpu().numpy())
        test_accuracy = accuracy_score(y_test.cpu().numpy(), test_predictions.cpu().numpy())

        # Calculate metrics for training data
        train_precision = precision_score(y_train.cpu().numpy(), train_predictions.cpu().numpy())
        train_recall = recall_score(y_train.cpu().numpy(), train_predictions.cpu().numpy())
        train_f1 = f1_score(y_train.cpu().numpy(), train_predictions.cpu().numpy())
        train_accuracy = accuracy_score(y_train.cpu().numpy(), train_predictions.cpu().numpy())

        print("\nModel Performance Metrics:")
        print(f"{'Metric':<10} {'Train':<10} {'Test':<10}")
        print(f"{'Loss':<10} {train_loss.item():<10.4f} {test_loss.item():<10.4f}")
        print(f"{'Accuracy':<10} {train_accuracy:<10.4f} {test_accuracy:<10.4f}")
        print(f"{'Precision':<10} {train_precision:<10.4f} {test_precision:<10.4f}")
        print(f"{'Recall':<10} {train_recall:<10.4f} {test_recall:<10.4f}")
        print(f"{'F1-score':<10} {train_f1:<10.4f} {test_f1:<10.4f}")

    # Output the device on which the model is running
    device = next(model.parameters()).device
    print(f"\nThe model is running on: {device}")
    
    return (train_precision, train_recall, train_f1, train_accuracy), (test_precision, test_recall, test_f1, test_accuracy)


#%%

#%%
# Load the saved model

# Verify the model is on the correct device

#%%

def simulate_and_analyze_trading_paths(test_precision, risk_2_reward, n_paths=100, n_steps=100, risk_per_trade=0.02):
    def simulate_path(hit_rate, risk_2_reward, risk_per_trade, n_steps):
        path = np.random.rand(n_steps)
        path = np.log1p(risk_per_trade*np.where(path > hit_rate, 1/risk_2_reward, -1))
        return np.expm1(path.cumsum())

    paths = [simulate_path(test_precision, risk_2_reward, risk_per_trade, n_steps) for _ in range(n_paths)]

    pd.DataFrame(paths).T.plot(figsize=(12, 6), alpha=0.1, legend=False)

    average_path = np.mean(paths, axis=0)
    plt.plot(average_path, color='red', linewidth=2, label='Average Path')

    plt.title(f'Simulated Trading Paths (Precision: {test_precision:.4f}, Reward/Risk: {1/risk_2_reward:.4f})')
    plt.xlabel('Steps')
    plt.ylabel('Cumulative Return')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    final_returns = [path[-1] for path in paths]
    print(f"Average final return: {np.mean(final_returns):.2f}")
    print(f"Median final return: {np.median(final_returns):.2f}")
    print(f"Standard deviation of final returns: {np.std(final_returns):.2f}")
    print(f"Percentage of profitable paths: {(np.sum([r > 0 for r in final_returns]) / n_paths * 100):.2f}%")

    return paths, final_returns




#%%
# Prepare data for BTC, 4h timeframe
exchange = 'binance'
asset = 'BTC'
quote = 'USDT'
timeframe = '6h'

df_all_normalized, df_ohlcv, normalized_columns = prepare_data(exchange, asset, quote, timeframe)

# Set up the device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

signal_kw = {
    'lookback_period': 8,
    'target_period': 6,
    'min_target_pct': 0.01,
    'risk_2_reward': 1 / 4
}
# Train the GRU model
model, (X_train, y_train), (X_test, y_test) = train_gru_model(df_ohlcv, df_all_normalized, device, get_signal, signal_kw)
# Evaluate the model


(train_precision, train_recall, train_f1, train_accuracy), (test_precision, test_recall, test_f1, test_accuracy) =  evaluate_model(model, X_train, y_train, X_test, y_test, device)
# Simulate trades with the acquired precision

paths, final_returns = simulate_and_analyze_trading_paths(test_precision, risk_2_reward, n_paths, n_steps, risk_per_trade)

# Additional analysis
print(f"\nAdditional Analysis:")
print(f"Max Drawdown: {np.min(paths):.2f}")
print(f"Best Path Return: {np.max(final_returns):.2f}")
print(f"Worst Path Return: {np.min(final_returns):.2f}")
print(f"Percentage of paths with >50% return: {(np.sum([r > 0.5 for r in final_returns]) / n_paths * 100):.2f}%")

#%%

model.save_state_dict('./models/GRU.pth')
model.load_state_dict(torch.load('./models/GRU.pth'))
#%%
#%%
#%%
#%%

#%%
#%%
#%%

#%%