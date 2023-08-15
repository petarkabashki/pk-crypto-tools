from .SampleBaseAgent import SampleBaseAgent
import pandas as pd
import numpy as np

class ExpectedSarsaAgent(SampleBaseAgent):
    _algorythm = 'ExpectedSarsa'


    # def __init__(self):
    #     super().__init__(self)

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