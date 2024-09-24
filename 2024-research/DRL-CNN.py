#%%
# %load_ext autoreload
# %autoreload 2
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import pandas_ta as ta
import math
from tqdm import tqdm
import gc
import time
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

# from pklib.rl import *


import gymnasium as gym  # Use Gymnasium instead of gym
from gymnasium.spaces import Discrete, Box

#%%


def split_dataframes(dataframes, train_size=0.7):
    """
    Split the input dataframes into training and testing sets.

    Parameters:
    dataframes (list): List of pandas DataFrames to split.
    train_size (float): Proportion of the data to use for training (default is 0.7).

    Returns:
    tuple: (train_dfs, test_dfs) Lists of DataFrames for training and testing.
    """
    train_dfs = []
    test_dfs = []

    for df in dataframes:
        # Calculate the split index
        split_index = int(len(df) * train_size)
        
        # Split the DataFrame
        train_df = df.iloc[:split_index]
        test_df = df.iloc[split_index:]
        
        # Append to the respective lists
        train_dfs.append(train_df)
        test_dfs.append(test_df)

    return train_dfs, test_dfs


def plot_cumulative_pnl(train_backtest_df, train_trades_df, test_backtest_df=None, test_trades_df=None):
    """
    Function to plot cumulative PnL for training and testing datasets on two separate axes.
    
    Parameters:
    - train_backtest_df: DataFrame containing the backtest results for the training dataset.
    - train_trades_df: DataFrame containing the trade details for the training dataset.
    - test_backtest_df: DataFrame containing the backtest results for the testing dataset (optional).
    - test_trades_df: DataFrame containing the trade details for the testing dataset (optional).
    """
    
    # Create a single figure with two separate axes (not sharing x-axis)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10))

    # Plot for the training dataset
    ax1.plot(train_backtest_df['cumulative_pnl'].apply(np.expm1))  # Plot cumulative PnL for training
    ax1.plot(np.append(train_backtest_df.index[:1],train_trades_df.exit_index), np.expm1(np.append(0,train_trades_df['pnl']).cumsum()), alpha=0.3, color='maroon', lw=3)  # Plot trade PnL
    ax1.set_ylabel('Cumulative PnL (Train)')
    ax1.set_title('TRAIN DATASET')  # Add a title for the training plot

    # Plot for the testing dataset (if provided)
    if test_backtest_df is not None:
        ax2.plot(test_backtest_df['cumulative_pnl'].apply(np.expm1))  # Plot cumulative PnL for testing
        ax2.plot(np.append(test_backtest_df.index[:1],test_trades_df.exit_index), np.expm1(np.append(0,test_trades_df['pnl']).cumsum()), alpha=0.3, color='maroon', lw=3)  # Plot trade PnL
        ax2.set_ylabel('Cumulative PnL (Test)')
        ax2.set_title('TEST DATASET')  # Add a title for the testing plot

    # Display the figure
    plt.tight_layout()
    plt.show()

    return fig, ax1, ax2

def perform_backtest(trainer, env):
    """
    Perform backtesting using the provided Ray RLlib-trained model on the test environment.
    
    Parameters:
    - trainer: A trained Ray RLlib agent (e.g., DQNTrainer).
    - env: An instance of TradingEnv, initialized with test data.
    
    Returns:
    - backtest_df: A pandas DataFrame containing the following columns:
        - 'logprice': Log price at each step.
        - 'position': Position held (1 for long, -1 for short, 0 for no position).
        - 'action': Action taken (e.g., 0 = hold, 1 = buy, 2 = sell).
        - 'cumulative_pnl': Cumulative PnL up to each step.
      The DataFrame is indexed by the original `df` index from `env`.
    """
    state, _ = env.reset()
    done = False

    # Initialize lists to store metrics
    positions = []
    actions = []
    cumulative_pnls = []
    indices = []
    trades = []

    # Initialize step counter based on lookback window
    step = env.lookback_window_size

    while not done and step < len(env.df):
        # Use Ray's trained model to compute the next action
        action = trainer.compute_single_action(state)

        # Take a step in the environment
        next_state, reward, done, truncated, info = env.step(action)

        # Log trades if any
        if 'trade_info' in info:
            trades.append(info['trade_info'])

        # Log metrics
        positions.append(info.get('position', 0))
        actions.append(action)
        cumulative_pnls.append(env.cumulative_pnl)

        # Collect the current index from the DataFrame
        current_index = env.df.index[step]
        indices.append(current_index)

        # Move to the next state
        state = next_state
        step += 1

    # Create a DataFrame with the collected metrics
    backtest_df = pd.DataFrame({
        'position': positions,
        'action': actions,
        'cumulative_pnl': cumulative_pnls
    }, index=indices)

    trades_df = pd.DataFrame(trades)

    if not trades_df.empty:
        # Map the entry and exit steps to the corresponding index in the logprice Series
        trades_df['entry_index'] = env.logprice.index[trades_df.entry_step]
        trades_df['exit_index'] = env.logprice.index[trades_df.exit_step]

        # Map the correct log prices based on the entry and exit indices
        trades_df['entry_logprice'] = env.logprice.iloc[trades_df.entry_step.values].values
        trades_df['exit_logprice'] = env.logprice.iloc[trades_df.exit_step.values].values
        trades_df['pnl'] = trades_df['position'] * (trades_df['exit_logprice'] - trades_df['entry_logprice'])

    return backtest_df, trades_df

#%%
import torch as T
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import os

class DeepQNetwork(nn.Module):
    def __init__(self, lr, n_actions, name, input_dims, chkpt_dir, conv_layers, fc_layers):

        """
        :param lr: Learning rate
        :param n_actions: Number of actions (output layer size)
        :param name: Name for saving checkpoints
        :param input_dims: Input dimensions (e.g., channels, lookback window size)
        :param chkpt_dir: Directory to save checkpoints
        :param conv_layers: List of dictionaries, each defining a conv layer (filters, kernel_size, stride, padding)
        :param fc_layers: List of integers, each defining the number of neurons in a fully connected layer
        """
        super(DeepQNetwork, self).__init__()
        
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.checkpoint_dir = chkpt_dir
        self.checkpoint_file = os.path.join(self.checkpoint_dir, name)

        # Dynamically create convolutional layers
        self.conv_layers = nn.ModuleList()
        in_channels = input_dims[0]  # Starting with the input channel

        for conv in conv_layers:
            self.conv_layers.append(
                nn.Conv1d(
                    in_channels,
                    conv['filters'],
                    kernel_size=conv['kernel_size'],
                    stride=conv['stride'],
                    padding=conv['padding']
                )
            )
            in_channels = conv['filters']  # Update the input channel for the next layer

        # Dynamically calculate the output of conv layers to adapt fully connected layers
        fc_input_dims = self.calculate_conv_output_dims(input_dims)

        # Dynamically create fully connected layers
        self.fc_layers = nn.ModuleList()
        fc_input = fc_input_dims
        for fc_dim in fc_layers:
            self.fc_layers.append(nn.Linear(fc_input, fc_dim))
            fc_input = fc_dim

        # Output layer for actions
        self.output_layer = nn.Linear(fc_input, n_actions)

        # Optimizer and loss function
        self.optimizer = optim.RMSprop(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()

        self.to(self.device)

    def calculate_conv_output_dims(self, input_dims):
        # Pass through the conv layers with a dummy input to compute the flattened output size
        state = T.zeros(1, *input_dims).to(self.device)
        for conv in self.conv_layers:
            state = conv(state)
        return int(np.prod(state.size()))

    def forward(self, state):
        x = state
        # Pass through all convolutional layers
        for conv in self.conv_layers:
            x = F.relu(conv(x))

        # Flatten the conv layer output for the fully connected layers
        x = x.view(x.size()[0], -1)

        # Pass through all fully connected layers
        for fc in self.fc_layers:
            x = F.relu(fc(x))

        # Output layer (actions)
        actions = self.output_layer(x)

        return actions

    def save_checkpoint(self):
        print('... saving checkpoint ...')
        T.save(self.state_dict(), self.checkpoint_file)

    def load_checkpoint(self):
        print('... loading checkpoint ...')
        self.load_state_dict(T.load(self.checkpoint_file))


#%%

import numpy as np

class ReplayBuffer(object):
    def __init__(self, max_size, input_shape, n_actions):
        self.mem_size = max_size
        self.mem_cntr = 0
        self.state_memory = np.zeros((self.mem_size, *input_shape),
                                     dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, *input_shape),
                                         dtype=np.float32)

        self.action_memory = np.zeros(self.mem_size, dtype=np.int64)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=bool)

    def store_transition(self, state, action, reward, state_, done):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.action_memory[index] = action
        self.reward_memory[index] = reward
        self.terminal_memory[index] = done
        self.mem_cntr += 1

    def sample_buffer(self, batch_size):
        max_mem = min(self.mem_cntr, self.mem_size)
        batch = np.random.choice(max_mem, batch_size, replace=False)

        states = self.state_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        states_ = self.new_state_memory[batch]
        terminal = self.terminal_memory[batch]

        return states, actions, rewards, states_, terminal
#%%
import collections
import cv2
import numpy as np
import matplotlib.pyplot as plt
import gymnasium as gym

def plot_learning_curve(x, scores, epsilons, filename, lines=None):
    fig=plt.figure()
    ax=fig.add_subplot(111, label="1")
    ax2=fig.add_subplot(111, label="2", frame_on=False)

    ax.plot(x, epsilons, color="C0")
    ax.set_xlabel("Training Steps", color="C0")
    ax.set_ylabel("Epsilon", color="C0")
    ax.tick_params(axis='x', colors="C0")
    ax.tick_params(axis='y', colors="C0")

    N = len(scores)
    running_avg = np.empty(N)
    for t in range(N):
	    running_avg[t] = np.mean(scores[max(0, t-20):(t+1)])

    ax2.scatter(x, running_avg, color="C1")
    ax2.axes.get_xaxis().set_visible(False)
    ax2.yaxis.tick_right()
    ax2.set_ylabel('Score', color="C1")
    ax2.yaxis.set_label_position('right')
    ax2.tick_params(axis='y', colors="C1")

    if lines is not None:
        for line in lines:
            plt.axvline(x=line)

    plt.savefig(filename)

class RepeatActionAndMaxFrame(gym.Wrapper):
    def __init__(self, env=None, repeat=4, clip_reward=False, no_ops=0,
                 fire_first=False):
        super(RepeatActionAndMaxFrame, self).__init__(env)
        self.repeat = repeat
        self.shape = env.observation_space.low.shape
        self.frame_buffer = np.zeros_like((2, self.shape))
        self.clip_reward = clip_reward
        self.no_ops = no_ops
        self.fire_first = fire_first

    def step(self, action):
        t_reward = 0.0
        done = False
        for i in range(self.repeat):
            obs, reward, done, info = self.env.step(action)
            if self.clip_reward:
                reward = np.clip(np.array([reward]), -1, 1)[0]
            t_reward += reward
            idx = i % 2
            self.frame_buffer[idx] = obs
            if done:
                break

        max_frame = np.maximum(self.frame_buffer[0], self.frame_buffer[1])
        return max_frame, t_reward, done, info

    def reset(self, seed, options):
        obs = self.env.reset(seed=seed, options=options)
        no_ops = np.random.randint(self.no_ops)+1 if self.no_ops > 0 else 0
        for _ in range(no_ops):
            _, _, done, _ = self.env.step(0)
            if done:
                self.env.reset()
        if self.fire_first:
            assert self.env.unwrapped.get_action_meanings()[1] == 'FIRE'
            obs, _, _, _ = self.env.step(1)

        self.frame_buffer = np.zeros_like((2,self.shape))
        self.frame_buffer[0] = obs

        return obs

class PreprocessFrame(gym.ObservationWrapper):
    def __init__(self, shape, env=None):
        super(PreprocessFrame, self).__init__(env)
        self.shape = (shape[2], shape[0], shape[1])
        self.observation_space = gym.spaces.Box(low=0.0, high=1.0,
                                    shape=self.shape, dtype=np.float32)

    def observation(self, obs):
        new_frame = cv2.cvtColor(obs, cv2.COLOR_RGB2GRAY)
        resized_screen = cv2.resize(new_frame, self.shape[1:],
                                    interpolation=cv2.INTER_AREA)
        new_obs = np.array(resized_screen, dtype=np.uint8).reshape(self.shape)
        new_obs = new_obs / 255.0

        return new_obs

class StackFrames(gym.ObservationWrapper):
    def __init__(self, env, repeat):
        super(StackFrames, self).__init__(env)
        self.observation_space = gym.spaces.Box(
                            env.observation_space.low.repeat(repeat, axis=0),
                            env.observation_space.high.repeat(repeat, axis=0),
                            dtype=np.float32)
        self.stack = collections.deque(maxlen=repeat)

    def reset(self, seed=None, options=None):
        self.stack.clear()
        observation = self.env.reset(seed=seed,options=options)
        for _ in range(self.stack.maxlen):
            self.stack.append(observation)

        return np.array(self.stack).reshape(self.observation_space.low.shape)

    def observation(self, observation):
        self.stack.append(observation)

        return np.array(self.stack).reshape(self.observation_space.low.shape)

def make_env(env_name, env_config, shape=(84,84,1), repeat=4, clip_rewards=False,
             no_ops=0, fire_first=False):
    env = gym.make(env_name,env_config=env_config)
    env = RepeatActionAndMaxFrame(env, repeat, clip_rewards, no_ops, fire_first)
    env = PreprocessFrame(shape, env)
    env = StackFrames(env, repeat)

    return env
#%%
import numpy as np
import torch as T
# from deep_q_network import DeepQNetwork
# from replay_memory import ReplayBuffer

class DQNAgent(object):
    def __init__(self, gamma, epsilon, lr, n_actions, input_dims,
                 mem_size, batch_size, eps_min=0.01, eps_dec=5e-7,
                 replace=1000, algo=None, env_name=None, chkpt_dir='tmp/dqn',env_config=None, conv_layers=None, fc_layers=None):
        self.gamma = gamma
        self.epsilon = epsilon
        self.lr = lr
        self.n_actions = n_actions
        self.input_dims = input_dims
        self.batch_size = batch_size
        self.eps_min = eps_min
        self.eps_dec = eps_dec
        self.replace_target_cnt = replace
        self.algo = algo
        self.env_name = env_name
        self.chkpt_dir = chkpt_dir
        self.action_space = [i for i in range(n_actions)]
        self.learn_step_counter = 0

        self.memory = ReplayBuffer(mem_size, input_dims, n_actions)

        self.q_eval = DeepQNetwork(self.lr, self.n_actions,
                                    input_dims=self.input_dims,
                                    name=self.env_name+'_'+self.algo+'_q_eval',
                                    chkpt_dir=self.chkpt_dir, conv_layers=conv_layers, fc_layers=fc_layers)

        self.q_next = DeepQNetwork(self.lr, self.n_actions,
                                    input_dims=self.input_dims,
                                    name=self.env_name+'_'+self.algo+'_q_next',
                                    chkpt_dir=self.chkpt_dir, conv_layers=conv_layers, fc_layers=fc_layers)

    def choose_action(self, observation):
        if np.random.random() > self.epsilon:
            state = T.tensor([observation],dtype=T.float).to(self.q_eval.device)
            actions = self.q_eval.forward(state)
            action = T.argmax(actions).item()
        else:
            action = np.random.choice(self.action_space)

        return action

    def store_transition(self, state, action, reward, state_, done):
        self.memory.store_transition(state, action, reward, state_, done)

    def sample_memory(self):
        state, action, reward, new_state, done = \
                                self.memory.sample_buffer(self.batch_size)

        states = T.tensor(state).to(self.q_eval.device)
        rewards = T.tensor(reward).to(self.q_eval.device)
        dones = T.tensor(done).to(self.q_eval.device)
        actions = T.tensor(action).to(self.q_eval.device)
        states_ = T.tensor(new_state).to(self.q_eval.device)

        return states, actions, rewards, states_, dones

    def replace_target_network(self):
        if self.learn_step_counter % self.replace_target_cnt == 0:
            self.q_next.load_state_dict(self.q_eval.state_dict())

    def decrement_epsilon(self):
        self.epsilon = self.epsilon - self.eps_dec \
                           if self.epsilon > self.eps_min else self.eps_min

    def save_models(self):
        self.q_eval.save_checkpoint()
        self.q_next.save_checkpoint()

    def load_models(self):
        self.q_eval.load_checkpoint()
        self.q_next.load_checkpoint()

    def learn(self):
        if self.memory.mem_cntr < self.batch_size:
            return

        self.q_eval.optimizer.zero_grad()

        self.replace_target_network()

        states, actions, rewards, states_, dones = self.sample_memory()
        indices = np.arange(self.batch_size)

        q_pred = self.q_eval.forward(states)[indices, actions]
        q_next = self.q_next.forward(states_).max(dim=1)[0]

        q_next[dones] = 0.0
        q_target = rewards + self.gamma*q_next

        loss = self.q_eval.loss(q_target, q_pred).to(self.q_eval.device)
        loss.backward()
        self.q_eval.optimizer.step()
        self.learn_step_counter += 1

        self.decrement_epsilon()
#%%
class TradingEnv(gym.Env):
    def __init__(self, env_config=None):
        self.df = env_config['df']
        self.logprice = env_config['logprice']
        self.lookback_window_size = env_config['lookback_window_size']
        self.trading_mode = env_config.get('trading_mode', 'both')
        self.verbosity = env_config.get('verbosity', 0)
        
        self.current_step = 0
        self.entry_logprice = None
        self.cumulative_pnl = 0
        self.num_positions = 0
        self.position = 0  # 1 = long, 0 = no position, -1 = short

        # Define action space based on trading mode
        if self.trading_mode == 'long_only':
            self.action_space = Discrete(2)  # 0 = hold, 1 = long
        elif self.trading_mode == 'short_only':
            self.action_space = Discrete(2)  # 0 = hold, 1 = short
        else:  # 'both'
            self.action_space = Discrete(4)  # 0 = hold, 1 = long, 2 = short, 3 = close position
        # self.action_space = Box(low=-np.inf, high=np.inf, shape=obs_space_shape, dtype=np.float32)
        # Observation space: OHLCV + technical indicators + entry price + position (flattened lookback period + 2 additional features)
        # obs_space_shape = (self.lookback_window_size * len(self.df.columns) + 1,)
        obs_space_shape = (len(self.df.columns) + 1, self.lookback_window_size )
        self.observation_space = Box(low=-np.inf, high=np.inf, shape=obs_space_shape, dtype=np.float32)
        
    def reset(self, seed=None, options=None):
        # Ensure enough data for the lookback window
        self.current_step = self.lookback_window_size

        self.entry_logprice = None
        self.cumulative_pnl = 0  # Reset cumulative PnL at the start of each episode
        self.position = 0  # Reset position
        self.num_positions = 0
        self.entry_step = None

        # Get the starting index for the lookback window (ensure it's valid)
        start_index = max(0, self.current_step - self.lookback_window_size)
        frame = self.df.iloc[start_index:self.current_step].values

        # Pad the history if there are fewer observations than the lookback size
        if len(frame) < self.lookback_window_size:
            padding = np.zeros((self.lookback_window_size - len(frame), len(self.df.columns)))
            frame = np.vstack((padding, frame))

        frame = np.hstack((frame, np.full((frame.shape[0],1), self.position))).astype(np.float32)
        # Return the initial flattened observation (1D array)
        # The 'info' dictionary is returned for compatibility with Gym environments
        # return np.hstack([initial_observation.flatten(),[0]]).astype(np.double), {'cumulative_pnl': self.cumulative_pnl}
        return frame.T, {'cumulative_pnl': self.cumulative_pnl}

    def step(self, action):
        current_logprice = self.logprice.iloc[self.current_step]
        reward = 0
        pnl = 0
        trade_info = {}

        if self.verbosity >= 1:
            print(f"Step: {self.current_step}, Action: {action}, Position: {self.position}, Cumulative PnL: {self.cumulative_pnl}")

        # Handle actions based on trading mode
        if self.trading_mode == 'long_only':
            if action == 1 and self.position == 0:  # Open long position
                self.entry_logprice = current_logprice
                self.position = 1
                self.entry_step = self.current_step
                if self.verbosity >= 2:
                    print(f"Opened long position at {current_logprice}")
            elif action == 0 and self.position == 1:  # Close long position
                if self.entry_logprice is not None:  # Check if entry price is set
                    pnl = current_logprice - self.entry_logprice
                    self.cumulative_pnl += pnl  # Accumulate PnL
                    self.num_positions += 1
                    trade_info = {
                        'trade_info': {
                            'entry_step': self.entry_step,
                            'exit_step': self.current_step,
                            'position': 1,
                            'pnl': pnl
                        }
                    }
                    if self.verbosity >= 2:
                        print(f"Closed long position. PnL: {pnl}")
                    self.position = 0
                    self.entry_step = None

        elif self.trading_mode == 'short_only':
            if action == 1 and self.position == 0:  # Open short position
                self.entry_logprice = current_logprice
                self.position = -1
                self.entry_step = self.current_step
                if self.verbosity >= 2:
                    print(f"Opened short position at {current_logprice}")
            elif action == 0 and self.position == -1:  # Close short position
                if self.entry_logprice is not None:  # Check if entry price is set
                    pnl = self.entry_logprice - current_logprice
                    self.cumulative_pnl += pnl  # Accumulate PnL
                    self.num_positions += 1
                    trade_info = {
                        'trade_info': {
                            'entry_step': self.entry_step,
                            'exit_step': self.current_step,
                            'position': -1,
                            'pnl': pnl
                        }
                    }
                    if self.verbosity >= 2:
                        print(f"Closed short position. PnL: {pnl}")
                    self.position = 0
                    self.entry_step = None

        elif self.trading_mode == 'both':
            if action == 1 and self.position != 1:  # Open or switch to long
                if self.position == -1 and self.entry_logprice is not None:  # Close short position first
                    pnl = self.entry_logprice - current_logprice
                    self.cumulative_pnl += pnl  # Accumulate PnL
                    self.num_positions += 1
                    trade_info = {
                        'trade_info': {
                            'entry_step': self.entry_step,
                            'exit_step': self.current_step,
                            'position': -1,
                            'pnl': pnl
                        }
                    }
                    if self.verbosity >= 2:
                        print(f"Switched from short to long. PnL: {pnl}")
                self.entry_logprice = current_logprice
                self.position = 1
                self.entry_step = self.current_step
                if self.verbosity >= 2:
                    print(f"Opened long position at {current_logprice}")

            elif action == 2 and self.position != -1:  # Open or switch to short
                if self.position == 1 and self.entry_logprice is not None:  # Close long position first
                    pnl = current_logprice - self.entry_logprice
                    self.cumulative_pnl += pnl  # Accumulate PnL
                    self.num_positions += 1
                    trade_info = {
                        'trade_info': {
                            'entry_step': self.entry_step,
                            'exit_step': self.current_step,
                            'position': 1,
                            'pnl': pnl
                        }
                    }
                    if self.verbosity >= 2:
                        print(f"Switched from long to short. PnL: {pnl}")
                self.entry_logprice = current_logprice
                self.position = -1
                self.entry_step = self.current_step
                if self.verbosity >= 2:
                    print(f"Opened short position at {current_logprice}")

            elif action == 3 and self.position != 0:  # Close position
                if self.entry_logprice is not None:  # Ensure entry price is set
                    pnl = self.position * (current_logprice - self.entry_logprice)
                    self.cumulative_pnl += pnl  # Accumulate PnL
                    self.num_positions += 1
                    trade_info = {
                        'trade_info': {
                            'entry_step': self.entry_step,
                            'exit_step': self.current_step,
                            'position': self.position,
                            'pnl': pnl
                        }
                    }
                    if self.verbosity >= 2:
                        print(f"Closed position. PnL: {pnl}")
                    self.position = 0
                    self.entry_step = None

        # Move to the next step
        self.current_step += 1
        terminated = self.current_step >= len(self.df) - 1  # End of data
        truncated = False

        # Handle termination case with open position
        if terminated and self.position != 0 and self.entry_logprice is not None:
            pnl = self.position * (current_logprice - self.entry_logprice)
            self.cumulative_pnl += pnl  # Accumulate PnL
            trade_info = {
                'trade_info': {
                    'entry_step': self.entry_step,
                    'exit_step': self.current_step,
                    'position': self.position,
                    'pnl': pnl
                }
            }
            if self.verbosity >= 2:
                print(f"Terminating with open position. Final PnL: {pnl}")
            self.position = 0  # Close position

        
        holding_penalty = 0
        if self.position != 0 and self.entry_step is not None:
            holding_duration = self.current_step - self.entry_step
            max_holding_duration = 50  # Define a threshold for holding too long
            if holding_duration > max_holding_duration:
                holding_penalty = (holding_duration - max_holding_duration) * 0.01  # Example penalty

        # Calculate the reward
        reward = pnl - holding_penalty  # Penalize for holding too long

        # Get the next observation
        obs = self._next_observation()

        # Return observation, reward, termination info, and trade details
        info = {
            'position': self.position,
            'cumulative_pnl': self.cumulative_pnl,
            **trade_info
        }

        return obs, reward, terminated, truncated, info

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

        frame = np.hstack((frame, np.full((frame.shape[0],1), self.position))).astype(np.float32)
        return frame.T
        # Return flattened lookback window and append position and entry price
        # return np.hstack([frame.flatten(), [self.position]]).astype(np.double)
    
    def render(self, mode="human"):
        # Print relevant information about the environment (for debugging purposes)
        print(f"Step: {self.current_step}, #Positions: {self.num_positions}, Cumulative PnL: {self.cumulative_pnl:.2f}")


def make_env(env_name, env_config, shape=(84,84,1), repeat=4, clip_rewards=False,
             no_ops=0, fire_first=False):
    env = gym.make(env_name,env_config=env_config)
    # env = RepeatActionAndMaxFrame(env, repeat, clip_rewards, no_ops, fire_first)
    # env = PreprocessFrame(shape, env)
    # env = StackFrames(env, repeat)

    return env
#%%


lookback_window_size = 7
trading_mode = 'long_only'# Wrap the environment

# params = {'conversion_periods': 110, 'base_periods': 301, 'lagging_span2_periods': 250, 'displacement': 180}
params = {'conversion_periods': 20, 'base_periods': 60, 'lagging_span2_periods': 120, 'displacement': 30}
# Parameters
exchange = 'binance'; asset = 'BTC'; quote = 'USDT'; nhours = 8
train_size= 0.7



df = load_candles(exchange, asset, quote, '8h').ffill().bfill()
# df = df.resample(f'{nhours}H').agg({'open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'}).ffill().bfill()
df.drop('volume', axis=1)
# add_ichimoku_cloud_indicator(df, params)
add_bollinger_bands(df, periods=[9,14,21,50], multiplier=2)
# add_rsi_columns(df,periods=[9,14,21])
# add_adx_columns(df,periods=[9,14,21])
# add_mom_columns(df,periods=[3,5,7,9,14,21,50,100])
# add_ema_columns(df,periods=[3,5,7,9,7,14,21,50,100])
# add_sma_columns(df,periods=[3,5,7,9,7,14,21,50,100])
# add_std_columns(df,periods=[3,5,7,9,7,14,21])
# log_price_over_ma_columns(df,periods=[3,5,9,14,21,50])
# add_sma_columns(df,periods=[14,21,50,100,200])
# add_std_columns(df,periods=[14,21,50,100,200])
# add_donchian_columns(df,periods=[9,14,21,50])
# add_rolling_max_columns(df,periods=[3,5,7,9,7,14,21,50,100], column="close")
# add_rolling_min_columns(df,periods=[3,5,7,9,7,14,21,50,100], column="close")
add_rolling_max_columns(df,periods=[9,14,21,50], column="high")
add_rolling_min_columns(df,periods=[9,14,21,50], column="low")

add_shifted_columns(df, periods=[14,21,50,100,200,400], columns=['open','high','low','close'], suffix="_SH")

df = df.dropna()
# df = df['2021':]#.iloc[:10000]
print(f'DF shape: {df.shape}')
df_logprice = df.close.apply(np.log).ffill().bfill()

(train_df_features, train_df_log_prices), (test_df_features, test_df_log_prices) = split_dataframes([df, df_logprice], train_size=train_size)
df

n_train,n_features = train_df_features.shape

#%%
# train_df_features

#%%

from gymnasium.envs.registration import register

register(
    id='TradingEnv-v0',   # Unique id for the environment
    entry_point=TradingEnv,
    # entry_point='__main__:TradingEnv',  # Path to the custom environment
    # max_episode_steps=200,  # Optional: max number of steps per episode
)

# Step 3: Create the environment using gymnasium.make
# env = gym.make('TradingEnv-v0')

train_env_config = {
    'df': train_df_features,  # Your training features DataFrame
    'logprice': train_df_log_prices,  # Your log prices
    'lookback_window_size': lookback_window_size,
    'trading_mode': trading_mode,  # or 'short_only', 'both'
    'verbosity': 0
}
test_env_config = {
    'df': test_df_features,  # Your training features DataFrame
    'logprice': test_df_log_prices,  # Your log prices
    'lookback_window_size': lookback_window_size,
    'trading_mode': trading_mode,  # or 'short_only', 'both'
    'verbosity': 0
}

# env = train_env = TradingEnv(train_env_config)

env = make_env('TradingEnv-v0',env_config=train_env_config)

observation_shape = env.observation_space.shape
print("Observation shape:", observation_shape)

#env = gym.make('CartPole-v1')
best_score = -np.inf
load_checkpoint = False
n_games = 20
# agent = Agent(lr=0.05, input_dims=env.observation_space.shape,
#                 n_actions=env.action_space.n, epsilon=1, eps_min=0.01, eps_dec=5e-6, hidden_layers=[128,128])
agent = DQNAgent(gamma=0.99, epsilon=1, lr=0.003,
                 input_dims=observation_shape,
                 n_actions=env.action_space.n, mem_size=5000, eps_min=0.1,
                 batch_size=32, replace=1000, eps_dec=1e-5,
                 chkpt_dir='models/', algo='DQNAgent',
                 env_name='TradingEnv-v0', env_config=train_env_config,
                 conv_layers = [
                    {'filters': 32, 'kernel_size': 4, 'stride': 4, 'padding': 1},
                    {'filters': 64, 'kernel_size': 3, 'stride': 2, 'padding': 1},
                    {'filters': 128, 'kernel_size': 2, 'stride': 1, 'padding': 1}
                ],
                fc_layers = [256, 256])

if load_checkpoint:
    agent.load_models()

fname = agent.algo + '_' + agent.env_name + '_lr' + str(agent.lr) +'_' \
        + str(n_games) + 'games'
figure_file = 'plots/' + fname + '.png'
# if you want to record video of your agent playing, do a mkdir tmp && mkdir tmp/dqn-video
# and uncomment the following 2 lines.
#env = wrappers.Monitor(env, "tmp/dqn-video",
#                    video_callable=lambda episode_id: True, force=True)
n_steps = 0
scores, eps_history, steps_array, pnls = [], [], [], []

for i in range(n_games):
    done = False
    observation, _ = env.reset()

    score = 0
    while not done:
        action = agent.choose_action(observation)
        observation_, reward, done, truncated, info = env.step(action)
        score += reward

        if not load_checkpoint:
            agent.store_transition(observation, action,
                                  reward, observation_, done)
            agent.learn()
        observation = observation_
        n_steps += 1
    scores.append(score)
    steps_array.append(n_steps)
    pnls.append(env.cumulative_pnl)

    avg_score = np.mean(scores[-100:])
    print('episode: ', i,'score %.4f' % score, 'cum_pnl  %.2f' % env.cumulative_pnl,
          ' average score %.1f' % avg_score, 'best score %.2f' % best_score,
        'epsilon %.2f' % agent.epsilon, 'steps', n_steps)

    if avg_score > best_score:
        if not load_checkpoint:
            agent.save_models()
        best_score = avg_score

    eps_history.append(agent.epsilon)

x = [i+1 for i in range(len(scores))]
plot_learning_curve(steps_array, scores, eps_history, figure_file)

#%%

# env.observation_space.shape

#%%

#%%

#%%

#%%

