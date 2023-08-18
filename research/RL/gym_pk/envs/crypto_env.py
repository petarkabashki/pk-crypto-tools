import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from gymnasium.spaces import Tuple, Discrete

from .trading_env import TradingEnv, Actions, Positions
from sklearn import preprocessing

class CryptoEnv(gym.Env):

    def __init__(self, prices, signal_features, future_prices, render_mode=None):
        
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.prices = prices
        self.state_features = signal_features
        self.future_prices = future_prices

        self._start_tick = 0
        self._end_tick = len(self.prices) - 1
        self._terminated = None
        self._position_history = None
        self._total_reward = None
        self._total_profit = None

        self.trade_fee = 0.002  # unit
        self.action_space = spaces.Discrete(3)

        le = preprocessing.LabelEncoder()
        le_fits = [le.fit(signal_features[c]) for c in signal_features.columns]
        le_dims = [le_.classes_.shape[0] for le_ in le_fits]
        self.observation_space = Tuple([Discrete(n) for n in le_dims])

        self.state_features = pd.DataFrame({
                signal_features.columns[i] : le_fits[i].transform(signal_features.iloc[:,i]) for i in range(len(le_fits))
            }, index=signal_features.index)


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self._terminated = False
        self._current_tick = self._start_tick
        # self._last_trade_tick = self._current_tick - 1
        # self._position_history = (self.window_size * [None]) + [self._position]
        self._total_reward = 0.
        self._total_profit = 1.  # unit
        # self._first_rendering = True
        self.history = {}

        info = self._get_info()
        observation = self._get_observation()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        self._terminated = False

        current_future_prices = self.future_prices.iloc[self._current_tick, :]
        r2r = 0.5
        target = 0.05
        step_reward = 0
        if action == 0:
            step_reward = 0
        else:
            action_dir = 1 if action == 1 else -1
            if action_dir == 1:
                step_reward = int(current_future_prices.fu_max_ret > target) + int(current_future_prices.fu_min_ret > -target * r2r)
            elif action_dir == -1:
                step_reward = int(current_future_prices.fu_min_ret < -target) + int(current_future_prices.fu_max_ret < target * r2r)

            # lret = np.log(current_hidden_.close / current_hidden_.open) * action_dir 
            # reward = int(lret > 0.05)
            # reward = (lret > 0.01) - 2 * (lret < 0) * abs(lret)
            # reward = -1 +  2*(current_hidden_.cdir == action_dir) + int(lret > 0.01)
            # reward = np.log(current_hidden_.close / current_hidden_.open) * action_dir - 0.002

        self._current_tick += 1

        
        if self._current_tick == self._end_tick:
            self._terminated = True
        # self.current_state = self.obs_states[self.current_t]        

        # if self.current_state[0] == 0 and self.current_state[1] > 0:
        #     if self.current_state[1] < self.cols - 1:
        #         reward = -100.0
        #         self.current_state = deepcopy(self.start)
        #     else:
        #         is_terminal = True

        # self.reward_obs_term = (reward, self.observation(self.current_state), is_terminal)

        # return self.reward_obs_term
        ###############

        self._total_reward += step_reward

        observation = self._get_observation()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, step_reward, self._terminated, False, info


    def _get_observation(self):
        return tuple(self.state_features.iloc[self._current_tick,:].values)

    def _get_info(self):
        return dict(
            total_reward = self._total_reward,
            total_profit = self._total_profit,
            # position = self._position.value
        )
    # def _process_data(self):
    #     prices = self.df.loc[:, 'close'].to_numpy()

    #     prices[self.frame_bound[0] - self.window_size]  # validate index (TODO: Improve validation)
    #     prices = prices[self.frame_bound[0]-self.window_size:self.frame_bound[1]]

    #     diff = np.insert(np.diff(prices), 0, 0)
    #     signal_features = np.column_stack((prices, diff))

    #     return prices, signal_features


    # def _calculate_reward(self, action):
    #     step_reward = 0  # pip

    #     trade = False
    #     if ((action == Actions.Buy.value and self._position == Positions.Short) or
    #         (action == Actions.Sell.value and self._position == Positions.Long)):
    #         trade = True

    #     if trade:
    #         current_price = self.prices[self._current_tick]
    #         last_trade_price = self.prices[self._last_trade_tick]
    #         price_diff = current_price - last_trade_price

    #         if self._position == Positions.Short:
    #             step_reward += -price_diff * 10000
    #         elif self._position == Positions.Long:
    #             step_reward += price_diff * 10000

    #     return step_reward


    # def _update_profit(self, action):
    #     trade = False
    #     if ((action == Actions.Buy.value and self._position == Positions.Short) or
    #         (action == Actions.Sell.value and self._position == Positions.Long)):
    #         trade = True

    #     if trade or self._terminated:
    #         current_price = self.prices[self._current_tick]
    #         last_trade_price = self.prices[self._last_trade_tick]

    #         if self.unit_side == 'left':
    #             if self._position == Positions.Short:
    #                 quantity = self._total_profit * (last_trade_price - self.trade_fee)
    #                 self._total_profit = quantity / current_price

    #         elif self.unit_side == 'right':
    #             if self._position == Positions.Long:
    #                 quantity = self._total_profit / last_trade_price
    #                 self._total_profit = quantity * (current_price - self.trade_fee)


    # def max_possible_profit(self):
    #     current_tick = self._start_tick
    #     last_trade_tick = current_tick - 1
    #     profit = 1.

    #     while current_tick <= self._end_tick:
    #         position = None
    #         if self.prices[current_tick] < self.prices[current_tick - 1]:
    #             while (current_tick <= self._end_tick and
    #                    self.prices[current_tick] < self.prices[current_tick - 1]):
    #                 current_tick += 1
    #             position = Positions.Short
    #         else:
    #             while (current_tick <= self._end_tick and
    #                    self.prices[current_tick] >= self.prices[current_tick - 1]):
    #                 current_tick += 1
    #             position = Positions.Long

    #         current_price = self.prices[current_tick - 1]
    #         last_trade_price = self.prices[last_trade_tick]

    #         if self.unit_side == 'left':
    #             if position == Positions.Short:
    #                 quantity = profit * (last_trade_price - self.trade_fee)
    #                 profit = quantity / current_price

    #         elif self.unit_side == 'right':
    #             if position == Positions.Long:
    #                 quantity = profit / last_trade_price
    #                 profit = quantity * (current_price - self.trade_fee)

    #         last_trade_tick = current_tick - 1

    #     return profit
