#!/usr/bin/env python

from .BaseEnvironment import BaseEnvironment
import numpy as np
# from math import 


class TradeEnvironment(BaseEnvironment):
    """Implements the environment for an RLGlue environment

    Note:
        env_init, env_start, env_step, env_cleanup, and env_message are required
        methods.
    """

    # def __init__(self):


    def env_init(self, env_info={}):
        """Setup for the environment called when the experiment first starts.

        Note:
            Initialize a tuple with the reward, first state observation, boolean
            indicating if it's terminal.
        """
        self.current_state = None

    def env_start(self, env_start_info={}):
        """The first method called when the episode starts, called before the
        agent starts.

        Returns:
            The first state observation from the environment.
        """
        self.obs_states = env_start_info['obs_states']
        self.hidden_states = env_start_info['hidden_states']
        self.current_t = 0  # An empty NumPy array
        self.current_state = self.obs_states.iloc[self.current_t]

        self.reward_obs_term = (0.0, self.observation(self.current_state), False)

        return self.reward_obs_term[1]

    def env_step(self, action):
        """A step taken by the environment.

        Args:
            action: The action taken by the agent

        Returns:
            (float, state, Boolean): a tuple of the reward, state observation,
                and boolean indicating if it's terminal.
        """


        current_hidden_ = self.hidden_states.iloc[self.current_t, :]
        r2r = 0.5
        target = 0.05
        reward = 0
        if action == 0:
            reward = 0
        else:
            action_dir = 1 if action == 1 else -1
            if action_dir == 1:
                reward = int(current_hidden_.fu_max_ret > target) + int(current_hidden_.fu_min_ret > -target * r2r)
            elif action_dir == -1:
                reward = int(current_hidden_.fu_min_ret < -target) + int(current_hidden_.fu_max_ret < target * r2r)

            # lret = np.log(current_hidden_.close / current_hidden_.open) * action_dir 
            # reward = int(lret > 0.05)
            # reward = (lret > 0.01) - 2 * (lret < 0) * abs(lret)
            # reward = -1 +  2*(current_hidden_.cdir == action_dir) + int(lret > 0.01)
            # reward = np.log(current_hidden_.close / current_hidden_.open) * action_dir - 0.002

        self.current_t += 1
        self.current_state = self.obs_states[self.current_t]        
        is_terminal = (self.current_t == self.obs_states.shape[0] - 1)

        # if self.current_state[0] == 0 and self.current_state[1] > 0:
        #     if self.current_state[1] < self.cols - 1:
        #         reward = -100.0
        #         self.current_state = deepcopy(self.start)
        #     else:
        #         is_terminal = True

        self.reward_obs_term = (reward, self.observation(self.current_state), is_terminal)

        return self.reward_obs_term

    def observation(self, state):
        return state #state.ncudir_L1 + 10 * state.ncudir_L2 + 100 * state.ncudir_L3 + 1000 * state.ncudir_L4

    def env_cleanup(self):
        """Cleanup done after the environment ends"""
        pass

    def env_message(self, message):
        """A message asking the environment for information

        Args:
            message (string): the message passed to the environment

        Returns:
            string: the response (or answer) to the message
        """
        if message == "what is the current reward?":
            return "{}".format(self.reward_obs_term[0])

        # else
        return "I don't know how to respond to your message"
