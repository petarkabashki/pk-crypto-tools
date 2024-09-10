import numpy as np
import gymnasium as gym  # Use Gymnasium instead of gym
from gymnasium.spaces import Discrete, Box
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def is_lower_than_thresholds(val, thresholds):
    return [val < threshold for threshold in thresholds]


class TradingEnv(gym.Env):
    def __init__(self, df, logprice, lookback_window_size=10):
        super(TradingEnv, self).__init__()
        
        self.df = df
        self.logprice = logprice
        self.lookback_window_size = lookback_window_size
        
        self.current_step = 0
        self.entry_logprice = None
        self.cumulative_pnl = 0
        self.num_positions = 0
        self.position = 0  # 1 = long, 0 = no position, -1 = short

        # Define action space: 0 = hold, 1 = long, 2 = short, 3 = close position
        self.action_space = Discrete(3)

        # Observation space: OHLCV + technical indicators + entry price + position (flattened lookback period + 2 additional features)
        obs_space_shape = (lookback_window_size * len(self.df.columns) + 2,)
        self.observation_space = Box(low=-np.inf, high=np.inf, shape=obs_space_shape, dtype=np.float32)

    def reset(self, seed=None, options=None):
        self.current_step = self.lookback_window_size  # Start after enough steps for lookback
        self.entry_logprice = None
        self.cumulative_pnl = 0
        self.position = 0  # Reset position
        self.num_positions = 0
        self.entry_step = None

        # Initialize the buffer with the lookback window of observations for the starting point
        start_index = max(0, self.current_step - self.lookback_window_size)
        initial_observation = self.df.iloc[start_index:self.current_step].values

        # Pad the history if there are fewer observations than the lookback size
        if len(initial_observation) < self.lookback_window_size:
            padding = np.zeros((self.lookback_window_size - len(initial_observation), len(self.df.columns)))
            initial_observation = np.vstack((padding, initial_observation))

        # Return the initial flattened observation (1D array) with position and entry price
        return np.hstack([initial_observation.flatten(), [self.position], self.get_broken_unrealized_thresholds()]).astype(np.float32), {'cumulative_pnl': 0}

    def step(self, action):
        current_logprice = self.logprice.iloc[self.current_step]
        reward = 0
        pnl = 0
        trade_info = {}
        
        # Open a long position if action is 1 and no position is currently held
        if action == 1 and self.position == 0:  
            self.entry_logprice = current_logprice
            self.position = 1  # Set position to long
            self.entry_step = self.current_step

        # Close position if action is 2 and a position is currently held
        elif action == 2 and self.position != 0:  
            pnl = self.position * (current_logprice - self.entry_logprice)
            self.cumulative_pnl += pnl
            self.position = 0  # Close position
            self.num_positions += 1

            # Log trade info
            trade_info = {
                'trade_info': {
                    'entry_step': self.entry_step,
                    'exit_step': self.current_step,
                    'pnl': pnl  # Profit or loss for the trade
                }
            }
            self.entry_step = None

        # Move to the next step
        self.current_step += 1
        terminated = self.current_step >= len(self.df) - 1  # Terminate if we reached the end of the data
        truncated = False  # You can set this based on some condition like max steps, if needed
        
        # Close any open positions if the episode terminates
        if terminated and self.position != 0:
            pnl = self.position * (current_logprice - self.entry_logprice)
            self.cumulative_pnl += pnl
            trade_info = {
                'trade_info': {
                    'entry_step': self.entry_step,
                    'exit_step': self.current_step,
                    'pnl': pnl  # Profit or loss for the final trade
                }
            }
            self.position = 0  # Close the final position
        
        # Calculate reward as pnl or penalize if no position
        reward = pnl
        penalty = 0.05 if self.position == 0 else 0.0  # Encourage taking positions
        reward -= penalty

        # Clip reward to avoid excessive values (optional)
        reward = np.clip(reward, -1, 1)

        # Get next observation
        obs = self._next_observation()
        
        # Return observation, reward, termination info, and trade details
        info = {
            'position': self.position,
            'cumulative_pnl': self.cumulative_pnl,
            **trade_info
        }

        return obs, reward, terminated, truncated, info

    
    def get_unrealized(self):
        if self.position == 0:
            return 0
        return self.position * (self.logprice.iloc[self.current_step] - self.entry_logprice)
    
    def get_broken_unrealized_thresholds(self):
        pct_unrealized = np.expm1(self.get_unrealized())
        thresholds = [-0.5,-0.2,-0.1,-0.05,-0.02, -0.01, 0]
        return is_lower_than_thresholds(pct_unrealized, thresholds) + is_lower_than_thresholds(-pct_unrealized, thresholds)
        
    def _next_observation(self):
        # Handle edge cases where the current step is less than the lookback window size
        start_index = max(0, self.current_step - self.lookback_window_size)
        frame = self.df.iloc[start_index:self.current_step]

        # If the lookback window is smaller than the full lookback size, pad with earlier rows
        if len(frame) < self.lookback_window_size:
            padding = np.zeros((self.lookback_window_size - len(frame), len(self.df.columns)))
            frame = np.vstack((padding, frame.values))
        else:
            frame = frame.values

        # Return flattened lookback window and append position and entry price
        return np.hstack([frame.flatten(), [self.position], self.get_broken_unrealized_thresholds()]).astype(np.float32)

    def render(self):
        current_logprice = self.logprice.iloc[self.current_step]
        # position_str = "Long" if self.position == 1 else ("Short" if self.position == -1 else "No position")
        print(f"Step: {self.current_step}, # Positions: {self.num_positions}, Cumulative PnL%: {100*np.expm1(self.cumulative_pnl):.2f}")
        

class SARSAOptTabularAgent:
    def __init__(self, env, epsilon=0.5, alpha=0.3, gamma=0.99, min_epsilon=0.01, epsilon_decay=0.995, early_stopping_steps=1000):
        self.env = env
        self.epsilon = epsilon  # Initial exploration rate
        self.min_epsilon = min_epsilon  # Minimum exploration rate
        self.epsilon_decay = epsilon_decay  # Decay rate for epsilon
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor

        # Early stopping params
        self.early_stopping_steps = early_stopping_steps  # Stop if no improvement in this many steps
        self.best_performance = -float('inf')
        self.no_improvement_counter = 0
        self.total_steps = 0  # Track total steps taken across episodes

        # Initialize a Q-table as a dictionary
        self.q_table = {}

    def get_q_value(self, state, action):
        state_action_key = (tuple(state.flatten()), action)
        return self.q_table.get(state_action_key, 0)

    def update_q_value(self, state, action, new_q_value):
        state_action_key = (tuple(state.flatten()), action)
        self.q_table[state_action_key] = new_q_value

    def choose_action(self, state, use_exploration=True):
        # Epsilon-greedy action selection
        if use_exploration and np.random.random() < self.epsilon:
            return self.env.action_space.sample()  # Explore
        else:
            q_values = [self.get_q_value(state, a) for a in range(self.env.action_space.n)]
            return np.argmax(q_values)


    def early_stopping(self, cumulative_reward):
        """
        Implement early stopping if the agent's performance doesn't improve for several steps.
        """
        if cumulative_reward > self.best_performance:
            self.best_performance = cumulative_reward
            self.no_improvement_counter = 0
        else:
            self.no_improvement_counter += 1

        if self.no_improvement_counter >= self.early_stopping_steps:
            print(f'Early stopping triggered after {self.no_improvement_counter} steps without improvement.')
            return True
        return False

    def train(self, num_steps=10000):
        """
        Train the agent using the SARSA algorithm, applying optimizations based on steps.
        """
        cumulative_reward = 0  # Track cumulative reward for early stopping

        while self.total_steps < num_steps:
            # Reset the environment and get the initial state
            state, _ = self.env.reset()
            episode_steps = 0  # Track steps within the episode

            # Choose the initial action
            action = self.choose_action(state)

            done = False

            while not done and self.total_steps < num_steps:
                # Take a step in the environment
                next_state, reward, done, truncated, info = self.env.step(action)

                # Choose the next action using epsilon-greedy strategy
                next_action = self.choose_action(next_state)

                # SARSA update: Q(s, a) <- Q(s, a) + alpha * [r + gamma * Q(s', a') - Q(s, a)]
                current_q_value = self.get_q_value(state, action)
                next_q_value = self.get_q_value(next_state, next_action)
                new_q_value = current_q_value + self.alpha * (reward + self.gamma * next_q_value - current_q_value)

                # Update the Q-table
                self.update_q_value(state, action, new_q_value)

                # Accumulate rewards
                cumulative_reward += reward
                self.total_steps += 1  # Increment global step count
                episode_steps += 1  # Increment episode step count

                # Check for early stopping based on steps
                if self.early_stopping(cumulative_reward):
                    return

                # Move to the next state and action
                state = next_state
                action = next_action

            # Print progress at the end of each episode
            self.env.render()
            print(f'Episode Steps: {episode_steps}, Global Steps: {self.total_steps}, Cumulative PnL(log): {self.env.cumulative_pnl:.2f}, Epsilon: {self.epsilon:.4f}')



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
    ax2.plot(test_backtest_df.cumulative_pnl.apply(np.expm1))  # Plot cumulative PnL for testing
    ax2.plot(test_trades_df.exit_index, test_trades_df.pnl.cumsum().apply(np.expm1), alpha=0.3)  # Plot trade PnL
    ax2.set_ylabel('Cumulative PnL (Test)')
    ax2.set_title('TEST DATASET')  # Add a title for the testing plot

    # Display the figure
    plt.tight_layout()
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
    trades_df['pnl'] = trades_df['exit_logprice'] - trades_df['entry_logprice']


    return backtest_df, trades_df


def train_test_split(df, log_prices, train_size=0.8):
    """
    Split the data into training and testing sets based on a time-based split.
    
    Parameters:
    - df (pd.DataFrame): DataFrame containing the features (e.g., df_comp_features).
    - log_prices (pd.Series): Series containing the log prices (aligned with df).
    - train_size (float): The proportion of data to use for training (default is 0.8).
    
    Returns:
    - train_df: Training set of features.
    - test_df: Testing set of features.
    - train_log_prices: Training set of log prices.
    - test_log_prices: Testing set of log prices.
    """
    # Determine the split point
    split_index = int(len(df) * train_size)
    
    # Split the feature DataFrame
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]
    
    # Split the log prices Series
    train_log_prices = log_prices.iloc[:split_index]
    test_log_prices = log_prices.iloc[split_index:]
    
    return train_df, test_df, train_log_prices, test_log_prices

