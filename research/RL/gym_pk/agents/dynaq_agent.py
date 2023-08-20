
from __future__ import annotations

from collections import defaultdict

import numpy as np
from gymnasium import spaces
# import gymnasium as gym


class DynaQAgent:

    algo = 'DynaQ'
    def _info(self):
        return F"{self.algo}: {self.aparams}"

    def __init__(
        self,
        action_space: spaces.Space,
        # state_space: spaces.Space,
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
        # self.state_space = state_space
        self.aparams = aparams

        self.q_values = defaultdict(lambda: np.zeros(self.action_space.n))

        self.dynaqplus = aparams['dynaqplus']
        self.planning_steps = aparams['planning_steps']
        self.alpha = aparams['alpha']
        self.gamma = aparams['gamma']

        self.epsilon = aparams['initial_epsilon']
        self.epsilon_decay = aparams['epsilon_decay']
        self.final_epsilon = aparams['final_epsilon']

        self.model = defaultdict(lambda: {})
        self.planning_rand_generator = np.random.RandomState(aparams.get('planning_seed', 42))

        if self.dynaqplus:
            self.kappa = aparams.get("kappa", 0.001)
            # self.tau = np.zeros((self.state_space.n, self.action_space.n))
            self.tau = defaultdict(lambda: np.zeros(self.action_space.n))

        self.training_error = []

    def start_episode(self, obs):
        pass

    def planning_step(self):
        """performs planning, i.e. indirect RL.

        Args:
            None
        Returns:
            Nothing
        """
        
        # The indirect RL step:
        # - Choose a state and action from the set of experiences that are stored in the model. (~2 lines)
        # - Query the model with this state-action pair for the predicted next state and reward.(~1 line)
        # - Update the action values with this simulated experience.                            (2~4 lines)
        # - Repeat for the required number of planning steps.
        #
        # Note that the update equation is different for terminal and non-terminal transitions. 
        # To differentiate between a terminal and a non-terminal next state, assume that the model stores
        # the terminal state as a dummy state like -1
        #
        # Important: remember you have a random number generator 'planning_rand_generator' as 
        #     a part of the class which you need to use as self.planning_rand_generator.choice()
        #     For the sake of reproducibility and grading, *do not* use anything else like 
        #     np.random.choice() for performing search control.

        # ----------------
        # your code here
        for _ in range(self.planning_steps):
            past_obs = self.planning_rand_generator.choice(list(self.model.keys()))
            past_action = self.planning_rand_generator.choice(list(self.model[past_obs].keys()))
            state, reward = self.model[past_obs][past_action]
            if self.dynaqplus:
                reward += self.kappa * np.sqrt(self.tau[past_obs][past_action])

            future_q_value = (state != -1) * np.max(self.q_values[state])
            temporal_difference = (
                reward + self.gamma * future_q_value - self.q_values[past_obs][past_action]
            )

            self.q_values[past_obs][past_action] = (
                self.q_values[past_obs][past_action] + self.alpha * temporal_difference
            )

    def get_action(self, obs: tuple[int, int, bool]) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        # with probability epsilon return a random action to explore the environment
        if np.random.random() < self.epsilon:
            return self.action_space.sample()

        # with probability (1 - epsilon) act greedily (exploit)
        else:
            return int(np.argmax(self.q_values[obs]))

    def update_model(self, past_obs, past_action, state, reward):
        """updates the model 
        
        Args:
            past_obs       (int): s
            past_action      (int): a
            state            (int): s'
            reward           (int): r
        Returns:
            Nothing
        """
        # Update the model with the (s,a,s',r) tuple (1~4 lines)
        
        # ----------------
        # your code here
       
        self.model[past_obs][past_action] = (state, reward)

    def update(
        self,
        obs: tuple[int, int, bool],
        action: int,
        reward: float,
        terminated: bool,
        next_obs: tuple[int, int, bool],
    ):
        if self.dynaqplus:
            for s in self.tau: self.tau[s] += 1
            # self.tau += 1
            self.tau[obs][action] = 0

        """Updates the Q-value of an action."""
        future_q_value = (not terminated) * np.max(self.q_values[next_obs])
        temporal_difference = (
            reward + self.gamma * future_q_value - self.q_values[obs][action]
        )

        self.q_values[obs][action] = (
            self.q_values[obs][action] + self.alpha * temporal_difference
        )

        self.training_error.append(temporal_difference)

        if terminated: next_obs = -1
        self.update_model(obs, action, next_obs, reward)
        self.planning_step()

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)