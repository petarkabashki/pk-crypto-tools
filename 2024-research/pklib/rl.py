import numpy as np
import gymnasium as gym  # Use Gymnasium instead of gym
from gymnasium.spaces import Discrete, Box
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import pickle

def is_lower_than_thresholds(val, thresholds):
    return [val < threshold for threshold in thresholds]



def plot_cumulative_pnl(train_backtest_df, train_trades_df, test_backtest_df, test_trades_df):
    """
    Function to plot cumulative PnL for training and testing datasets on two separate axes.
    
    Parameters:
    - train_backtest_df: DataFrame containing the backtest results for the training dataset.
    - train_trades_df: DataFrame containing the trade details for the training dataset.
    - test_backtest_df: DataFrame containing the backtest results for the testing dataset.
    - test_trades_df: DataFrame containing the trade details for the testing dataset.
    """
    
    # Create a single figure with two separate axes (not sharing x-axis)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10))

    # Plot for the training dataset
    ax1.plot(train_backtest_df.cumulative_pnl.apply(np.expm1))  # Plot cumulative PnL for training
    ax1.plot(train_trades_df.exit_index, train_trades_df.pnl.cumsum().apply(np.expm1), alpha=0.3)  # Plot trade PnL
    ax1.set_ylabel('Cumulative PnL (Train)')
    ax1.set_title('TRAIN DATASET')  # Add a title for the training plot

    # Plot for the testing dataset
    if test_backtest_df is not None:
        ax2.plot(test_backtest_df.cumulative_pnl.apply(np.expm1))  # Plot cumulative PnL for testing
        ax2.plot(test_trades_df.exit_index, test_trades_df.pnl.cumsum().apply(np.expm1), alpha=0.3)  # Plot trade PnL
        ax2.set_ylabel('Cumulative PnL (Test)')
    ax2.set_title('TEST DATASET')  # Add a title for the testing plot

    # Display the figure
    plt.tight_layout()
    return fig, ax1, ax2
    plt.show()


def perform_backtest(agent, env):
    """
    Perform backtesting using the provided agent on the test environment.
    
    Parameters:
    - agent: An instance of SARSATabularAgent, already trained.
    - env: An instance of TradingEnv, initialized with test data.
    
    Returns:
    - backtest_df: A pandas DataFrame containing the following columns:
        - 'logprice': Log price at each step.
        - 'position': Position held (1 for long, -1 for short, 0 for no position).
        - 'action': Action taken (e.g., 0 = hold, 1 = buy, 2 = sell).
        - 'unrealized_pnl': Unrealized PnL at each step.
        - 'realized_pnl': Realized PnL at each step.
        - 'cumulative_pnl': Cumulative PnL up to each step.
      The DataFrame is indexed by the original `df` index from `env`.
    """
    # Reset the test environment to get the initial state
    state, _ = env.reset()
    done = False

    # Initialize lists to store metrics
    positions = []
    actions = []
    unrealized_pnls = []
    realized_pnls = []
    cumulative_pnls = []
    # logprices = []
    indices = []
    trades = []

    # Initialize tracking variable for realized PnL
    realized_pnl_prev = 0.0

    # Initialize step counter based on lookback window
    # Assuming that after reset, the current_step is set to lookback_window_size
    step = env.lookback_window_size

    while not done and step < len(env.df):
        # Choose action using the agent's policy (ensure greedy policy during backtest)
        action = agent.choose_action(state, use_exploration=False)

        # Take a step in the environment
        next_state, reward, done, truncated, info = env.step(action)
        if 'trade_info' in info:
            trades.append(info['trade_info'])

        # Collect metrics
        positions.append(info.get('position', 0))  # Default to 0 if 'position' not in info
        actions.append(action)
        unrealized_pnls.append(env.get_unrealized())
        realized_pnl_step = env.cumulative_pnl - realized_pnl_prev
        realized_pnls.append(realized_pnl_step)
        cumulative_pnls.append(env.cumulative_pnl)
        # logprices.append(test_env.logprice.iloc[step])

        # Collect the current index from the DataFrame
        current_index = env.df.index[step]
        indices.append(current_index)

        # Update realized_pnl_prev for the next step
        realized_pnl_prev = env.cumulative_pnl

        # Move to the next state
        state = next_state

        # Increment the step counter
        step += 1

    # Create a DataFrame with the collected metrics
    backtest_df = pd.DataFrame({
        # 'logprice': logprices,
        'position': positions,
        'action': actions,
        'unrealized_pnl': unrealized_pnls,
        'realized_pnl': realized_pnls,
        'cumulative_pnl': cumulative_pnls
    }, index=indices)
    
    trades_df = pd.DataFrame(trades)

    # Map the entry and exit steps to the corresponding index in the logprice Series
    trades_df['entry_index'] = env.logprice.index[trades_df.entry_step]
    trades_df['exit_index'] = env.logprice.index[trades_df.exit_step]

    # Now, map the correct log prices based on the entry and exit indices
    trades_df['entry_logprice'] = env.logprice.iloc[trades_df.entry_step.values].values
    trades_df['exit_logprice'] = env.logprice.iloc[trades_df.exit_step.values].values
    trades_df['pnl'] = trades_df['position'] * (trades_df['exit_logprice'] - trades_df['entry_logprice'])


    return backtest_df, trades_df


