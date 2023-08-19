
from __future__ import annotations

from collections import defaultdict
from .base_agent import BaseAgent
import numpy as np
from gymnasium.spaces import Space
# import gymnasium as gym


class MonteCarloAgent(BaseAgent):

    algo = 'Monte-Carlo'

    def _info(self):
        return f'{self.algo}, first_visit:{self.first_visit}, exploring_starts:{self.exploring_starts_spec}, gamma:{self.gamma}'
    
    def __init__(
        self,
        action_space: Space,
        gamma,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        first_visit: bool = True,
        exploring_starts_q = None,

        # learning_rate: float,
        # initial_epsilon: float,
        # epsilon_decay: float,   
        # final_epsilon: float,
        # discount_factor: float = 0.95,
        #  = None
    ):
        """Initialize a Reinforcement Learning agent with an empty dictionary
        of state-action values (q_values), a learning rate and an epsilon.

        Args:
            learning_rate: The learning rate
            initial_epsilon: The initial epsilon value
            epsilon_decay: The decay for epsilon
            final_epsilon: The final epsilon value
            discount_factor: The discount factor for computing the Q-value
        """
        super().__init__(action_space)
        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon
        self.first_visit = first_visit
        self.exploring_starts_q = exploring_starts_q
        self.gamma = gamma

        self.N = defaultdict(lambda: np.zeros(self.action_space.n))
        # self.returns_sum = defaultdict(lambda: np.zeros(self.action_space.n))
        # self.action_space = action_space
        # self.q_values = {}
        if exploring_starts_q is not None:
            # print('aaaaaaaa', exploring_starts_spec['q_value'])
            self.q_values = defaultdict(lambda: np.full(self.action_space.n, exploring_starts_q))
        else:
            self.q_values = defaultdict(lambda: np.zeros(self.action_space.n))

        # self.lr = learning_rate
        # self.discount_factor = discount_factor

        # self.epsilon = initial_epsilon
        # self.epsilon_decay = epsilon_decay
        # self.final_epsilon = final_epsilon

        # self.training_error = []

    def start_episode(self):
        # print('Starting episode')
        self.episode = []


    def get_action(self, obs: tuple[int, int, bool]) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        q = self.q_values[obs]
        if self.epsilon is not None:
            # with probability epsilon return a random action to explore the environment
            if np.random.random() < self.epsilon:
                # print('eps rand')
                return self.action_space.sample()

            # with probability (1 - epsilon) act greedily (exploit)
            else:
                # print('eps norm')
                return np.random.choice(np.flatnonzero(q == q.max())) 
        else:
            return np.random.choice(np.flatnonzero(q == q.max())) 
    
    def update(
        self,
        obs: tuple[int, int, bool],
        action: int,
        reward: float,
        terminated: bool,
        next_obs: tuple[int, int, bool],
    ):
        """Updates the Q-value of an action."""
        if self.first_visit:
            # print('appending')
            self.episode.append((obs, action, reward))

            # if terminated:
            #     for
        

        if self.first_visit:
            g = 0
            # epi_obs, epi_act, epi_rew = zip(*self.episode)
            # s_a_returns = defaultdict(lambda: [])

            # 
            for i in range(len(self.episode) - 1, -1, -1):
                s, a, r = self.episode[i]

                g = g * self.gamma + r
                i_sa_first = next(ii for ii, (s_,a_,r_) in enumerate(self.episode) if s == s_ and a == a_)

                if i_sa_first == i:
                    self.N[s][a] += 1.0
                    # print(self.q_values[s][a] , g / self.N[(s,a)], self.q_values[s][a] + g / self.N[(s,a)])
                    
                    # self.returns_sum[(s,a)] = self.returns_sum[(s,a)] + g / self.N[(s,a)]
                    self.q_values[s][a] = self.q_values[s][a] + g / self.N[s][a]
                    # s_a_returns[(s,a)].append(g)
                    # self.q_values[(s,a)] = np.average(s_a_returns[(s,a)])


        # future_q_value = (not terminated) * np.max(self.q_values[next_obs])
        # temporal_difference = (
        #     reward + self.discount_factor * future_q_value - self.q_values[obs][action]
        # )

        # self.q_values[obs][action] = (
        #     self.q_values[obs][action] + self.lr * temporal_difference
        # )
        # self.training_error.append(temporal_difference)
        # pass

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)