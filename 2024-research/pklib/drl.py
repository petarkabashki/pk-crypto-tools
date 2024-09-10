from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch as th
import torch.nn as nn
import numpy as np

# Custom feature extractor for the TradingEnv
class CustomFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 128):
        # Call the parent constructor to initialize the BaseFeaturesExtractor
        super(CustomFeatureExtractor, self).__init__(observation_space, features_dim)

        # The observation space shape should be compatible with the input of the feature extractor
        self.flatten = nn.Flatten()

        # Feature extraction network (simple MLP here)
        self.net = nn.Sequential(
            nn.Linear(np.prod(observation_space.shape), 256),  # Flatten the input first
            nn.ReLU(),
            nn.Linear(256, features_dim)  # The output dimension is the features_dim
        )

    def forward(self, observations: th.Tensor) -> th.Tensor:
        # Pass the observation through the feature extractor network
        return self.net(self.flatten(observations))

from stable_baselines3 import DQN
from stable_baselines3.dqn.policies import DQNPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

# Custom DQN Policy that uses the custom feature extractor
class CustomDQNPolicy(DQNPolicy):
    def __init__(self, observation_space, action_space, lr_schedule, net_arch=None, activation_fn=nn.ReLU, **kwargs):
        # Call the parent constructor to initialize DQNPolicy and set features_dim
        super(CustomDQNPolicy, self).__init__(observation_space, action_space, lr_schedule, net_arch, activation_fn, **kwargs)

        # The features are extracted by the custom feature extractor
        self.features_extractor = CustomFeatureExtractor(observation_space, features_dim=128)
        
        # Create the Q-network using the extracted features
        self.q_net = nn.Sequential(
            nn.Linear(self.features_extractor._features_dim, 128),  # First custom layer with 128 units
            nn.ReLU(),
            nn.Linear(128, 64),  # Second custom layer with 64 units
            nn.ReLU(),
            nn.Linear(64, self.action_space.n)  # Output layer with the number of actions
        )

    # Forward pass for the custom network
    def forward(self, obs):
        # Extract features using the custom feature extractor and pass through Q-network
        features = self.features_extractor(obs)
        return self.q_net(features)

    def _predict(self, obs, deterministic=False):
        q_values = self.forward(obs)
        if deterministic:
            return q_values.argmax(dim=1)
        else:
            return q_values

from stable_baselines3.common.callbacks import BaseCallback

class PnLLoggingCallback(BaseCallback):
    """
    Custom callback for logging cumulative PnL at each step.
    """
    def __init__(self, verbose=0):
        super(PnLLoggingCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        # Access the `info` dictionary from the environment at the current step
        infos = self.locals.get('infos', None)

        if infos is not None:
            # Assuming the environment returns cumulative_pnl in the info dictionary
            for info in infos:
                if 'cumulative_pnl' in info:
                    pnl = info['cumulative_pnl']
                    # Log cumulative PnL
                    self.logger.record('cumulative_pnl', pnl)

        return True


class CustomLoggingCallback(BaseCallback):
    def _on_step(self) -> bool:
        # Log exploration rate
        self.logger.record('exploration_rate', self.model.exploration_rate)
        
        # Log learning rate
        self.logger.record('learning_rate', self.model.learning_rate)
        
        # Log scaled rewards (if you're scaling them manually)
        scaled_reward = self.locals['rewards'][0]
        self.logger.record('scaled_reward', scaled_reward)
        
        return True



class LearningRateScheduler(BaseCallback):
    def __init__(self, initial_lr=0.0001, decay_rate=0.99, verbose=0):
        super(LearningRateScheduler, self).__init__(verbose)
        self.initial_lr = initial_lr
        self.decay_rate = decay_rate

    def _on_step(self) -> bool:
        """Update the learning rate on each step."""
        lr = self.initial_lr * (self.decay_rate ** self.num_timesteps)
        self.model.learning_rate = lr
        if self.verbose > 0:
            print(f"Step: {self.num_timesteps}, Learning Rate: {lr}")
        return True

class AdaptiveLearningRate(BaseCallback):
    def __init__(self, initial_lr=0.0001, reward_threshold=100, lr_increase=1.05, lr_decrease=0.95, verbose=0):
        super(AdaptiveLearningRate, self).__init__(verbose)
        self.initial_lr = initial_lr
        self.reward_threshold = reward_threshold
        self.lr_increase = lr_increase
        self.lr_decrease = lr_decrease
        self.episode_rewards = []  # To store rewards for the current episode
        self.last_mean_reward = 0

    def _on_step(self) -> bool:
        """Called at every step of the environment to update rewards."""
        # Accumulate the rewards for the current episode
        self.episode_rewards.append(self.locals['rewards'][0])

        # Check if the episode has terminated
        if self.locals.get('dones', None) is not None and self.locals['dones'][0]:
            # Calculate the mean reward for the episode
            current_mean_reward = sum(self.episode_rewards) / len(self.episode_rewards)
            self.episode_rewards = []  # Reset for the next episode

            # Adjust the learning rate based on the reward improvement
            if current_mean_reward > self.last_mean_reward + self.reward_threshold:
                # Increase learning rate
                self.model.learning_rate = min(self.model.learning_rate * self.lr_increase, 1e-3)  # Prevent too high LR
            elif current_mean_reward < self.last_mean_reward - self.reward_threshold:
                # Decrease learning rate
                self.model.learning_rate = max(self.model.learning_rate * self.lr_decrease, 1e-5)  # Prevent too low LR

            self.last_mean_reward = current_mean_reward

            if self.verbose > 0:
                print(f"Step: {self.num_timesteps}, Learning Rate: {self.model.learning_rate}, Mean Reward: {current_mean_reward}")

        return True


class VarianceRewardScaler(BaseCallback):
    def __init__(self, window_size=100, epsilon=1e-6, verbose=0):
        """
        Variance-based reward scaler to normalize rewards based on recent reward variance.

        :param window_size: The size of the window to track recent rewards.
        :param epsilon: A small value to prevent division by zero.
        :param verbose: Level of verbosity, 0 for silent, 1 for logging.
        """
        super(VarianceRewardScaler, self).__init__(verbose)
        self.window_size = window_size
        self.epsilon = epsilon
        self.recent_rewards = deque(maxlen=window_size)  # Stores the recent rewards
        self.scaled_rewards = []

    def _on_step(self) -> bool:
        """
        This function is called after each environment step.
        """
        reward = self.locals['rewards'][0]  # Get the current step's reward

        # Store the reward
        self.recent_rewards.append(reward)

        # Calculate variance only if we have enough data
        if len(self.recent_rewards) >= self.window_size:
            reward_mean = np.mean(self.recent_rewards)
            reward_variance = np.var(self.recent_rewards)

            # Scale the reward by dividing by the variance (avoid division by zero with epsilon)
            scaled_reward = reward / (np.sqrt(reward_variance) + self.epsilon)
            self.scaled_rewards.append(scaled_reward)

            # Replace the original reward with the scaled reward
            self.locals['rewards'][0] = scaled_reward

            if self.verbose > 0:
                print(f"Step: {self.num_timesteps}, Original Reward: {reward}, Scaled Reward: {scaled_reward}, Variance: {reward_variance}")
        else:
            # Use the original reward if not enough data for variance calculation
            self.scaled_rewards.append(reward)

        return True

    def _on_training_end(self) -> None:
        """
        This function is called when training ends.
        """
        if self.verbose > 0:
            print(f"Final Scaled Rewards: {self.scaled_rewards}")
            
            
            
import numpy as np
import pandas as pd
from collections import deque
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO

class RewardNormalizer:
    def __init__(self, epsilon=1e-8):
        self.mean = 0
        self.var = 1
        self.epsilon = epsilon
        self.count = 1

    def normalize(self, reward):
        self.mean = self.mean * (self.count / (self.count + 1)) + reward / (self.count + 1)
        self.var = self.var * (self.count / (self.count + 1)) + (reward - self.mean) ** 2 / (self.count + 1)
        self.count += 1
        return (reward - self.mean) / (np.sqrt(self.var) + self.epsilon)
    
def clip_reward(reward, min_val=-1, max_val=1):
    """Clip the reward to the range [min_val, max_val]."""
    return np.clip(reward, min_val, max_val)

def scale_reward(reward, scaling_factor=100):
    """Scale the reward by a fixed factor to normalize it."""
    return reward / scaling_factor


reward_normalizer = RewardNormalizer()

class TradingEnv(gym.Env):
    def __init__(self, df, logprice, lookback_window_size=10):
        super(TradingEnv, self).__init__()
        
        self.df = df
        self.logprice = logprice
        self.lookback_window_size = lookback_window_size
        
        self.current_step = 0
        self.entry_logprice = None
        self.cumulative_pnl = 0
        self.position = 0  # 1 = long, 0 = no position, -1 = short

        # Define action space: 0 = hold, 1 = long, 2 = short, 3 = close position
        self.action_space = spaces.Discrete(3)

        # Observation space: OHLCV + technical indicators + entry price + position (flattened lookback period + 2 additional features)
        obs_space_shape = (lookback_window_size * len(self.df.columns) + 2,)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=obs_space_shape, dtype=np.float32)

    def reset(self, seed=None, options=None):
        self.current_step = self.lookback_window_size  # Start after enough steps for lookback
        self.entry_logprice = None
        self.cumulative_pnl = 0
        self.position = 0  # Reset position

        # Initialize the buffer with the lookback window of observations for the starting point
        start_index = max(0, self.current_step - self.lookback_window_size)
        initial_observation = self.df.iloc[start_index:self.current_step].values

        # Pad the history if there are fewer observations than the lookback size
        if len(initial_observation) < self.lookback_window_size:
            padding = np.zeros((self.lookback_window_size - len(initial_observation), len(self.df.columns)))
            initial_observation = np.vstack((padding, initial_observation))

        # Return the initial flattened observation (1D array) with position and entry price
        return np.hstack([initial_observation.flatten(), [self.position, self.entry_logprice if self.entry_logprice else 0]]).astype(np.float32), {'cumulative_pnl': 0}

    def step(self, action):
        current_logprice = self.logprice.iloc[self.current_step]
        reward = 0
        pnl = 0
        is_entry = is_exit = 0
        
        if action == 1 and self.position == 0:  # Open or maintain long            
            self.entry_logprice = current_logprice  # New long entry
            self.position = 1  # Set position to long
            is_entry = 1

        elif action == 2 and self.position != 0:  # Close position
            pnl = self.position * (current_logprice - self.entry_logprice)
            self.cumulative_pnl += pnl
            self.position = 0  # No position
            is_exit = 1

        # if action == 1:  # Open or maintain long
        #     if self.position == -1:  # Close short
        #         pnl = self.position * (current_logprice - self.entry_logprice)
        #         self.cumulative_pnl += pnl

        #     self.entry_logprice = current_logprice  # New long entry
        #     self.position = 1  # Set position to long

        # elif action == 2:  # Open or maintain short
        #     if self.position == 1:  # Close long
        #         pnl = self.position * (current_logprice - self.entry_logprice)
        #         self.cumulative_pnl += pnl

        #     self.entry_logprice = current_logprice
        #     self.position = -1  # Set position to short

        # elif action == 3 and self.position != 0:  # Close position
        #     pnl = self.position * (current_logprice - self.entry_logprice)
        #     self.cumulative_pnl += pnl
        #     self.position = 0  # No position

        # Move to the next step
        self.current_step += 1
        terminated = self.current_step >= len(self.df) - 1  # Terminate if we reached the end of the data
        truncated = False  # You can set this based on some condition like max steps, if needed
        
        if terminated and self.position != 0:
            pnl = self.position * (current_logprice - self.entry_logprice)
            self.cumulative_pnl += pnl
            self.position = 0  # No position
            is_exit = 1

        # Assign reward based on pnl
        reward = pnl*10
        if reward < 0:
            reward *=5
        # reward = np.clip(reward, -1, 1)
        # reward = scale_reward(pnl)
        # reward = reward_normalizer.normalize(pnl)

        # Get next observation
        obs = self._next_observation()
        
        info = {
            'position': self.position,
            'cumulative_pnl': self.cumulative_pnl,
            'is_entry': is_entry,
            'is_exit': is_exit
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

        # Return flattened lookback window and append position and entry price
        return np.hstack([frame.flatten(), [self.position, self.entry_logprice if self.entry_logprice else 0]]).astype(np.float32)

    def render(self):
        current_logprice = self.logprice.iloc[self.current_step]
        position_str = "Long" if self.position == 1 else ("Short" if self.position == -1 else "No position")
        print(f"Step: {self.current_step}, LogPrice: {current_logprice:.2f}, Position: {position_str}, Entry LogPrice: {self.entry_logprice if self.entry_logprice else 'N/A'}, Cumulative PnL: {self.cumulative_pnl:.2f}")
