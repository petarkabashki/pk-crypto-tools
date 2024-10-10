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
import seaborn as sns
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
    stoploss = df[lookback_column].rolling(lookback_period).min()#.mul(0.995)
    
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
timeframe = '4h'
df = load_candles(exchange, asset, quote, timeframe)

# Define periods for moving averages and standard deviation
periods = [3, 5, 7, 10, 14, 17, 21, 30, 50, 80, 100, 200]

# Calculate indicators
indicators = {
    'SMA': calculate_talib_indicator(df, 'SMA', [{'timeperiod': p} for p in periods]),
    # 'EMA': calculate_talib_indicator(df, 'EMA', [{'timeperiod': p} for p in periods]),
    # 'STDDEV': calculate_talib_indicator(df, 'STDDEV', [{'timeperiod': p, 'nbdev': 1} for p in periods]),
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
normalized_columns = df_all_normalized.columns
normalized_columns = normalized_columns.tolist()

#%%
# df_all_normalized['open'] = 1e-8
# normalized_columns
# df_ohlcv
#%%


def print_performance_table(model, X, y, threshold=0.5, set_name=""):
    model.eval()
    with torch.no_grad():
        outputs = model(X)
        preds = (torch.sigmoid(outputs.squeeze()) > threshold).float()
        
        y_np = y.cpu().numpy()
        preds_np = preds.cpu().numpy()
        
        precision = precision_score(y_np, preds_np)
        recall = recall_score(y_np, preds_np)
        f1 = f1_score(y_np, preds_np)
        accuracy = accuracy_score(y_np, preds_np)
        cm = confusion_matrix(y_np, preds_np)

        metrics_table = [
            ["Metric", "Value"],
            ["Accuracy", f"{accuracy:.4f}"],
            ["Precision", f"{precision:.4f}"],
            ["Recall", f"{recall:.4f}"],
            ["F1-score", f"{f1:.4f}"]
        ]

        cm_table = [
            ["", "Predicted Negative", "Predicted Positive"],
            ["Actual Negative", cm[0][0], cm[0][1]],
            ["Actual Positive", cm[1][0], cm[1][1]]
        ]

        print(f"\n{set_name} Performance Metrics:")
        print(tabulate(metrics_table, headers="firstrow", tablefmt="grid"))

        print(f"\n{set_name} Confusion Matrix:")
        print(tabulate(cm_table, headers="firstrow", tablefmt="grid"))

    model.train()
    return precision, recall, f1

#%%

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim.lr_scheduler import StepLR, LambdaLR
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler, random_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from tabulate import tabulate
from imblearn.over_sampling import SMOTE
from torch.optim.lr_scheduler import OneCycleLR
class SimpleGRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.3):
        super(SimpleGRUModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.gru(x, h0)
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        return out

# Use the existing get_signal function with sample parameters
# Pre-declare arguments for get_signal function
lookback_period = 8
holding_period = 6
threshold = 0.01
direction = 2.5
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

# Assuming X and y are your full dataset
# First, split into train+val and test sets
X_train_val, X_test, y_train_val, y_test = train_test_split(X_seq, y_seq, test_size=0.2, random_state=42)

# Then split train+val into train and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.2, random_state=42)

# Convert to PyTorch tensors and move to the appropriate device
X_train = torch.FloatTensor(X_train).to(device)
y_train = torch.FloatTensor(y_train).to(device)
X_val = torch.FloatTensor(X_val).to(device)
y_val = torch.FloatTensor(y_val).to(device)
X_test = torch.FloatTensor(X_test).to(device)
y_test = torch.FloatTensor(y_test).to(device)

print("Label type:", y_train.dtype)
print("Unique labels:", torch.unique(y_train))
print("Label distribution:", torch.bincount(y_train.long()))

# Create DataLoader for training data
train_data = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)

#%%

#%%
# Initialize the model and move it to the appropriate device
input_size = X_train.shape[2]
print(f'input_size: {input_size}')

# Hyperparameters
hidden_size = 64
num_layers = 1
batch_size = 256  # Increased batch size
learning_rate = 0.001
num_epochs = 100
weight_decay = 1e-5
warmup_epochs = 5  # Number of epochs for warmup

# Initialize the model, criterion, and optimizer
model = SimpleGRUModel(input_size, hidden_size=hidden_size, num_layers=num_layers, output_size=1, dropout=0.3).to(device)

# Lower initial learning rate
initial_lr = 1e-4
optimizer = torch.optim.Adam(model.parameters(), lr=initial_lr, weight_decay=weight_decay)

# Learning rate scheduler with warmup
def warmup_lambda(epoch):
    if epoch < warmup_epochs:
        return float(epoch) / float(max(1, warmup_epochs))
    return 1.0

# scheduler = LambdaLR(optimizer, lr_lambda=warmup_lambda)

scheduler = OneCycleLR(optimizer, max_lr=0.01, epochs=num_epochs, steps_per_epoch=len(train_loader))

# Reshape X_train for SMOTE
X_train_reshaped = X_train.view(X_train.shape[0], -1).cpu().numpy()
y_train_np = y_train.cpu().numpy()

# Apply SMOTE
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_reshaped, y_train_np)

# Reshape back to sequence form
X_train_resampled = torch.FloatTensor(X_train_resampled.reshape(-1, sequence_length, input_size)).to(device)
y_train_resampled = torch.FloatTensor(y_train_resampled).to(device)

# Create new DataLoader with resampled data
train_data = TensorDataset(X_train_resampled, y_train_resampled)
train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)

# Class weights (if needed after SMOTE)
pos_weight = (y_train_resampled == 0).sum() / (y_train_resampled == 1).sum()
criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]).to(device))

# Dynamic threshold
def find_best_threshold(outputs, labels):
    best_threshold = 0
    best_f1 = 0
    for threshold in np.arange(0.1, 0.9, 0.1):
        preds = (torch.sigmoid(outputs) > threshold).float()
        f1 = f1_score(labels.cpu().numpy(), preds.cpu().numpy())
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    return best_threshold

# Training loop
best_val_f1 = 0
patience = 50
counter = 0
best_model = None
threshold = 0.5

for epoch in range(num_epochs):
    model.train()
    epoch_loss = 0.0
    
    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs.squeeze(), batch_y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        epoch_loss += loss.item()
    
    avg_train_loss = epoch_loss / len(train_loader)
    
    # Validation step
    model.eval()
    with torch.no_grad():
        val_outputs = model(X_val)
        threshold = find_best_threshold(val_outputs, y_val)
        val_preds = (torch.sigmoid(val_outputs.squeeze()) > threshold).float()
        val_f1 = f1_score(y_val.cpu().numpy(), val_preds.cpu().numpy())
        val_precision = precision_score(y_val.cpu().numpy(), val_preds.cpu().numpy())
    
    scheduler.step()
    
    if val_f1 > best_val_f1:
        best_val_f1 = val_f1
        counter = 0
        best_model = model.state_dict()
    else:
        counter += 1
        if counter >= patience:
            print(f'Early stopping at epoch {epoch+1}')
            break
    
    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {avg_train_loss:.6f}, '
          f'Val F1: {val_f1:.4f}, Val Precision: {val_precision:.4f}, '
          f'Threshold: {threshold:.4f}, LR: {optimizer.param_groups[0]["lr"]:.2e}')

# Load the best model
if best_model is not None:
    model.load_state_dict(best_model)
else:
    print("Warning: No best model was saved. Using the final model state.")
    
# Evaluation function
def print_combined_performance_table(model, X_train, y_train, X_test, y_test, threshold=0.5):
    model.eval()
    with torch.no_grad():
        # Training data evaluation
        train_outputs = model(X_train)
        train_preds = (torch.sigmoid(train_outputs.squeeze()) > threshold).float()
        
        # Test data evaluation
        test_outputs = model(X_test)
        test_preds = (torch.sigmoid(test_outputs.squeeze()) > threshold).float()
        
        # Convert to numpy for metric calculation
        y_train_np = y_train.cpu().numpy()
        train_preds_np = train_preds.cpu().numpy()
        y_test_np = y_test.cpu().numpy()
        test_preds_np = test_preds.cpu().numpy()
        
        # Calculate metrics
        train_accuracy = accuracy_score(y_train_np, train_preds_np)
        train_precision = precision_score(y_train_np, train_preds_np)
        train_recall = recall_score(y_train_np, train_preds_np)
        train_f1 = f1_score(y_train_np, train_preds_np)
        
        test_accuracy = accuracy_score(y_test_np, test_preds_np)
        test_precision = precision_score(y_test_np, test_preds_np)
        test_recall = recall_score(y_test_np, test_preds_np)
        test_f1 = f1_score(y_test_np, test_preds_np)

        # Calculate confusion matrices
        train_cm = confusion_matrix(y_train_np, train_preds_np)
        test_cm = confusion_matrix(y_test_np, test_preds_np)

        # Create combined table
        metrics_table = [
            ["Metric", "Training", "Test"],
            ["Accuracy", f"{train_accuracy:.4f}", f"{test_accuracy:.4f}"],
            ["Precision", f"{train_precision:.4f}", f"{test_precision:.4f}"],
            ["Recall", f"{train_recall:.4f}", f"{test_recall:.4f}"],
            ["F1-score", f"{train_f1:.4f}", f"{test_f1:.4f}"]
        ]

        print("\nModel Performance Metrics:")
        print(tabulate(metrics_table, headers="firstrow", tablefmt="grid"))

        # Create confusion matrix tables
        cm_table = [
            ["", "Training", "", "Test", ""],
            ["", "Predicted Negative", "Predicted Positive", "Predicted Negative", "Predicted Positive"],
            ["Actual Negative", train_cm[0][0], train_cm[0][1], test_cm[0][0], test_cm[0][1]],
            ["Actual Positive", train_cm[1][0], train_cm[1][1], test_cm[1][0], test_cm[1][1]]
        ]

        print("\nConfusion Matrices:")
        print(tabulate(cm_table, headers="firstrow", tablefmt="grid"))

    model.train()
    return train_precision, test_precision

# After training, call the function like this:
train_precision, test_precision = print_combined_performance_table(model, X_train, y_train, X_test, y_test, threshold)

#%%

# Evaluation
model.eval()
with torch.no_grad():
    # Test data evaluation
    test_outputs = model(X_test)
    test_loss = criterion(test_outputs.squeeze(), y_test)

    # Convert probabilities to binary predictions for test data
    test_predictions = (torch.sigmoid(test_outputs.squeeze()) > 0.5).float()

    # Training data evaluation
    train_outputs = model(X_train)
    train_loss = criterion(train_outputs.squeeze(), y_train)

    # Convert probabilities to binary predictions for training data
    train_predictions = (torch.sigmoid(train_outputs.squeeze()) > 0.5).float()

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

    # Create a table with train vs test metrics
    from tabulate import tabulate

    metrics_table = [
        ["Metric", "Train", "Test"],
        ["Loss", f"{train_loss.item():.4f}", f"{test_loss.item():.4f}"],
        ["Accuracy", f"{train_accuracy:.4f}", f"{test_accuracy:.4f}"],
        ["Precision", f"{train_precision:.4f}", f"{test_precision:.4f}"],
        ["Recall", f"{train_recall:.4f}", f"{test_recall:.4f}"],
        ["F1-score", f"{train_f1:.4f}", f"{test_f1:.4f}"]
    ]

    print("\nModel Performance Metrics:")
    print(tabulate(metrics_table, headers="firstrow", tablefmt="grid"))

# Output the device on which the model is running
device = next(model.parameters()).device
print(f"The model is running on: {device}")

#%%
# Feature importance analysis for GRU model

# First, we need to create a function to calculate feature importance
def calculate_feature_importance(model, X, y, n_iterations=10):
    feature_importance = torch.zeros(X.shape[2]).to(device)
    original_loss = nn.BCEWithLogitsLoss()(model(X).squeeze(), y)
    
    for feature in range(X.shape[2]):
        feature_losses = []
        for _ in range(n_iterations):
            X_permuted = X.clone()
            X_permuted[:, :, feature] = X_permuted[:, :, feature][torch.randperm(X.shape[0])]
            permuted_loss = nn.BCEWithLogitsLoss()(model(X_permuted).squeeze(), y)
            feature_losses.append(permuted_loss.item() - original_loss.item())
        
        feature_importance[feature] = torch.tensor(np.mean(feature_losses)).to(device)
    
    return feature_importance

# Calculate feature importance
with torch.no_grad():
    feature_importance = calculate_feature_importance(model, X_test, y_test)

# Normalize feature importance
normalized_importance = (feature_importance - feature_importance.min()) / (feature_importance.max() - feature_importance.min())

# Sort features by importance
sorted_idx = torch.argsort(normalized_importance, descending=True)
sorted_importance = normalized_importance[sorted_idx]

# Visualize feature importance
plt.figure(figsize=(10, 6))
plt.bar(range(len(sorted_importance)), sorted_importance.cpu().numpy())
plt.xlabel('Feature Index')
plt.ylabel('Normalized Importance')
plt.title('Feature Importance in GRU Model')
plt.tight_layout()
plt.show()

# Print top 10 most important features
print("Top 10 most important features:")
for i in range(10):
    print(f"Feature {sorted_idx[i].item()}: {sorted_importance[i].item():.4f}")

# y_test.sum(), y_train.sum()
#%%


def plot_feature_importance(model, feature_names, top_n=20):
    # Get the weights from the first layer of the model
    weights = model.gru.weight_ih_l0.detach().cpu().numpy()
    
    # Calculate the importance of each feature
    importance = np.sum(np.abs(weights), axis=0)
    
    # Sort features by importance
    sorted_idx = np.argsort(importance)
    sorted_importance = importance[sorted_idx]
    sorted_features = [feature_names[i] for i in sorted_idx]
    
    # Plot the top N features
    plt.figure(figsize=(12, 8))
    plt.barh(range(top_n), sorted_importance[-top_n:])
    plt.yticks(range(top_n), sorted_features[-top_n:])
    plt.xlabel('Feature Importance')
    plt.title(f'Top {top_n} Most Important Features')
    plt.tight_layout()
    plt.show()

# Assuming you have a list or array of feature names
feature_names = list(df_all_normalized.columns)  # Replace 'df' with your actual dataframe name

# After training the model
plot_feature_importance(model, feature_names, top_n=50)

# You can now call the function with a different top_n value if needed
# For example: plot_feature_importance(model, feature_names, top_n=30)

# ... rest of the code remains the same ...
#%%
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# Reshape X_train for SMOTE
X_train_reshaped = X_train.view(X_train.shape[0], -1).cpu().numpy()
y_train_np = y_train.cpu().numpy()

# Apply SMOTE
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_reshaped, y_train_np)

# Reshape back to sequence form
X_train_resampled = torch.FloatTensor(X_train_resampled.reshape(-1, sequence_length, input_size)).to(device)
y_train_resampled = torch.FloatTensor(y_train_resampled).to(device)

# Create new DataLoader with resampled data
train_data = TensorDataset(X_train_resampled, y_train_resampled)
train_loader = DataLoader(train_data, batch_size=256, shuffle=True)
#%%

#%%