
from __future__ import annotations

from collections import defaultdict
from math import sqrt

import numpy as np
from gymnasium import spaces
# import gymnasium as gym


class SarsaAgent:

    algo = 'SARSA'
    def _info(self):
        return F"{self.algo}: {self.aparams}"

    def __init__(
        self,
        action_space: spaces.Space,
        aparams,
        # learning_rate: float,
        # initial_epsilon: float,
        # epsilon_decay: float,
        # final_epsilon: float,
        # gamma: float = 0.95,
        
    ):
        """Initialize a Reinforcement Learning agent with an empty dictionary
        of state-action values (q_values), a learning rate and an epsilon.

        Args:
            learning_rate: The learning rate
            initial_epsilon: The initial epsilon value
            epsilon_decay: The decay for epsilon
            final_epsilon: The final epsilon value
            gamma: The discount factor for computing the Q-value
        """
        self.action_space = action_space
        self.aparams = aparams

        self.q_values = defaultdict(lambda: np.zeros(self.action_space.n))

        self.alpha = aparams['alpha']
        self.gamma = aparams['gamma']

        self.epsilon = aparams['initial_epsilon']
        self.epsilon_decay = aparams['epsilon_decay']
        self.final_epsilon = aparams['final_epsilon']
        self.expected_sarsa = aparams['expected_sarsa']
        self.next_action = None
        # self.t = 0

        self.training_error = []

    def start_episode(self, obs):
        self.next_action = self.calc_next_action(obs)

    def calc_next_action(self, obs):
        # with probability epsilon return a random action to explore the environment
        if np.random.random() < self.epsilon:
            return self.action_space.sample()

        # with probability (1 - epsilon) act greedily (exploit)
        else:
            q = self.q_values[obs]
            return np.random.choice(np.flatnonzero(q == q.max())) 
        
    def get_action(self, obs: tuple[int, int, bool]) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        # self.next_action = self.calc_next_action(obs)
        return self.next_action

    def update(
        self,
        obs: tuple[int, int, bool],
        action: int,
        reward: float,
        terminated: bool,
        next_obs: tuple[int, int, bool],
    ):
        """Updates the Q-value of an action."""
        if self.expected_sarsa:        
            ### Expected Sarsa
            # Not needed here, but for compliance with Normal Sarsa's calculations
            self.next_action = self.calc_next_action(next_obs)
            next_q = self.q_values[next_obs]
            next_q_max = np.max(next_q)
            expectation = (1- self.epsilon) * next_q_max + self.epsilon * np.mean(next_q)
            self.q_values[obs][action] += self.alpha * (reward + self.gamma * expectation - self.q_values[obs][action])
        else:
            ### Normal SARSA
            next_qval = 0
            if not terminated:
                self.next_action = self.calc_next_action(next_obs)
                next_qval = self.q_values[next_obs][self.next_action]

            qval = self.q_values[obs][action]
            temporal_difference = (
                reward + self.gamma * next_qval - qval
            )

            self.q_values[obs][action] = (
                qval + self.alpha * temporal_difference
            )
            self.training_error.append(temporal_difference)

        self.prev_action = action
        self.prev_obs = obs

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)