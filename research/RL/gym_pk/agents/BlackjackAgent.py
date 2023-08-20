
# %%


from collections import defaultdict
import numpy as np
from .base_agent import BaseAgent

class BlackjackAgent(BaseAgent):
    algo = "QLearning"
    def _info(self):
        return F"Blacjack QLearning: {self.aparams}"
    
    def __init__(
        self,
        action_space,
        aparams,
        # learning_rate: float,
        # initial_epsilon: float = 1,
        # epsilon_decay: float = 0.001,
        # final_epsilon: float = 0.01,
        # discount_factor: float = 0.95,
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
        self.aparams = aparams
        self.action_space = action_space
        self.q_values = defaultdict(lambda: np.zeros(self.action_space.n))

        self.lr = aparams['learning_rate']
        self.discount_factor = aparams['discount_factor'] if 'discount_factor' in aparams else 0.95

        self.epsilon = aparams['initial_epsilon']
        self.epsilon_decay = aparams['epsilon_decay']
        self.final_epsilon = aparams['final_epsilon']

        self.training_error = []


    def start_episode(self):
        pass

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

    def update(
        self,
        obs: tuple[int, int, bool],
        action: int,
        reward: float,
        terminated: bool,
        next_obs: tuple[int, int, bool],
    ):
        """Updates the Q-value of an action."""
        future_q_value = (not terminated) * np.max(self.q_values[next_obs])
        temporal_difference = (
            reward + self.discount_factor * future_q_value - self.q_values[obs][action]
        )

        self.q_values[obs][action] = (
            self.q_values[obs][action] + self.lr * temporal_difference
        )
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)