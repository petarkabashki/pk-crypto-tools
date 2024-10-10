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

# Load your data
from pklib.utilities import load_candles

exchange = 'binance'
asset = 'BTC'
quote = 'USDT'
timeframe = '8h'
df = load_candles(exchange, asset, quote, timeframe)

# Define periods for moving averages and standard deviation
periods = [3, 4, 5, 6, 7, 8, 9, 10, 14, 17, 21, 30, 50, 80, 100, 200]

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
normalized_columns
# df_ohlcv
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

# Use the existing get_signal function with sample parameters
# Pre-declare arguments for get_signal function
lookback_period = 8
holding_period = 6
threshold = 0.01
risk_2_reward = 1 / 3

# Call get_signal function with pre-declared arguments
y, _, _ = get_signal(df_ohlcv, lookback_period, holding_period, threshold, risk_2_reward=risk_2_reward)

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

#%%
# Initialize the model and move it to the appropriate device
input_size = X_train.shape[2]
print(f'input_size: {input_size}')

# Initialize the model, criterion, and optimizer
# hidden_size = input_size *2  # Set hidden size to twice the number of features
# fc_layers = [input_size // 2]  # Decreasing sizes based on input size
hidden_size = 256
fc_layers = [32]  
model = GRUModel(input_size, hidden_size=hidden_size, num_layers=1, fc_layers=fc_layers, output_size=1, dropout=0.2).to(device)


# Increase the weight for the positive class
pos_weight = torch.tensor([(len(y_train) - y_train.sum()) / y_train.sum() * 2]).to(device)  # Multiply by 2 or more
# criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

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
    return 1.0

scheduler = LambdaLR(optimizer, lr_lambda=warmup_lambda)
# scheduler = CosineAnnealingLR(optimizer, T_max=100, eta_min=1e-6)
# scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10, factor=0.1, min_lr=1e-6)
# Add gradient norm tracking
grad_norms = []

# Add this before the training loop
accumulation_steps = 5  # Adjust as needed

# Modify the training loop
num_epochs = 300
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



# Evaluation
model.eval()
with torch.no_grad():
    # Test data evaluation
    test_outputs = model(X_test)
    test_loss = criterion(test_outputs.squeeze(), y_test)
    print(f'Test Loss: {test_loss.item():.4f}')

    # Convert probabilities to binary predictions for test data
    test_predictions = (torch.sigmoid(test_outputs.squeeze()) > 0.5).float()
    
    # Compute confusion matrix for test data
    test_conf_matrix = confusion_matrix(y_test.cpu().numpy(), test_predictions.cpu().numpy())
    print("Test Confusion Matrix:")
    print(test_conf_matrix)

    # Training data evaluation
    train_outputs = model(X_train)
    train_loss = criterion(train_outputs.squeeze(), y_train)
    print(f'Train Loss: {train_loss.item():.4f}')

    # Convert probabilities to binary predictions for training data
    train_predictions = (torch.sigmoid(train_outputs.squeeze()) > 0.5).float()
    
    # Compute confusion matrix for training data
    train_conf_matrix = confusion_matrix(y_train.cpu().numpy(), train_predictions.cpu().numpy())
    print("Train Confusion Matrix:")
    print(train_conf_matrix)

    # Check class distribution
    print("Class distribution:")
    print(y_train.sum().item() / len(y_train))

    # If imbalanced, consider using class weights
    pos_weight = torch.tensor([(len(y_train) - y_train.sum()) / y_train.sum()]).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

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

    # Visualize the confusion matrices
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,4))
    
    sns.heatmap(test_conf_matrix, annot=True, fmt='d', cmap='Blues', ax=ax1)
    ax1.set_xlabel('Predicted')
    ax1.set_ylabel('Actual')
    ax1.set_title('Test Confusion Matrix')
    
    sns.heatmap(train_conf_matrix, annot=True, fmt='d', cmap='Blues', ax=ax2)
    ax2.set_xlabel('Predicted')
    ax2.set_ylabel('Actual')
    ax2.set_title('Train Confusion Matrix')
    
    plt.tight_layout()
    plt.show()

# Output the device on which the model is running
device = next(model.parameters()).device
print(f"The model is running on: {device}")

#%%
#%%

#%%
n_paths = 100
n_steps = 100
risk_per_trade = 0.02
# Function to simulate a single trading path
def simulate_path(hit_rate, risk_2_reward, risk_per_trade, n_steps):
    path = np.random.rand(n_steps)
    path = np.log1p(risk_per_trade*np.where(path > hit_rate, 1/risk_2_reward, -1))
    return np.expm1(path.cumsum())

# Simulate paths
paths = [simulate_path(test_precision, risk_2_reward, risk_per_trade, n_steps) for _ in range(n_paths)]

# Plot the simulated paths
# plt.figure(figsize=(12, 6))
# for path in paths:
#     plt.plot(path, alpha=0.1, color='blue')
pd.DataFrame(paths).T.plot(figsize=(12, 6), alpha=0.1, legend=False)

# Plot the average path
average_path = np.mean(paths, axis=0)
plt.plot(average_path, color='red', linewidth=2, label='Average Path')

plt.title(f'Simulated Trading Paths (Precision: {test_precision:.4f}, Reward/Risk: {1/risk_2_reward:.4f})')
plt.xlabel('Steps')
plt.ylabel('Cumulative Return')
# plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Print summary statistics
final_returns = [path[-1] for path in paths]
print(f"Average final return: {np.mean(final_returns):.2f}")
print(f"Median final return: {np.median(final_returns):.2f}")
print(f"Standard deviation of final returns: {np.std(final_returns):.2f}")
print(f"Percentage of profitable paths: {(np.sum([r > 0 for r in final_returns]) / n_paths * 100):.2f}%")


#%%

#%%
#%%
#%%
#%%
#%%

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