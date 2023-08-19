from .SampleBaseAgent import SampleBaseAgent
import pandas as pd
import numpy as np

from collections import defaultdict

class ExpectedSarsaAgent(SampleBaseAgent):

    def __init__(
        self,
        learning_rate: float,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        discount_factor: float = 0.95,
        action_space = None
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
        self.action_space = action_space

        self.q_values = defaultdict(lambda: np.zeros(self.action_space.n))

        self.lr = learning_rate
        self.discount_factor = discount_factor

        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        self.training_error = []

    def agent_start(self, observation):
        """The first method called when the episode starts, called after
        the environment starts.
        Args:
            observation (int): the state observation from the
                environment's evn_start function.
        Returns:
            action (int): the first action the agent takes.
        """
        
        # Choose action using epsilon greedy.
        state = observation
        # current_q = self._q[state, :]
        # if self.rand_generator.rand() < self.epsilon:
        #     action = self.rand_generator.randint(self.num_actions)
        # else:
        #     action = self.argmax(current_q)
        action = self.chose_action(state)
        self.prev_state = state
        self.prev_action = action
        return action
    
    def agent_step_update(self, state, reward):
        current_q = self._q[state,:]
        
        q_max = np.max(current_q)
        pi = np.ones(self.num_actions) * (self.epsilon / self.num_actions)
        pi += (current_q == q_max) * ((1 - self.epsilon) / np.sum(current_q == q_max))
        expectation = np.sum(current_q * pi)
        self._q[self.prev_state, self.prev_action] += self.step_size * (reward + self.discount * expectation - self._q[self.prev_state, self.prev_action])

    def agent_end_update(self, reward):
        self._q[self.prev_state, self.prev_action] += self.step_size * (reward - self._q[self.prev_state, self.prev_action])

    def argmax(self, q_values):
        """argmax with random tie-breaking
        Args:
            q_values (Numpy array): the array of action-values
        Returns:
            action (int): an action with the highest value
        """
        top = float("-inf")
        ties = []

        for i in range(len(q_values)):
            if q_values[i] > top:
                top = q_values[i]
                ties = []

            if q_values[i] == top:
                ties.append(i)

        return self.rand_generator.choice(ties)