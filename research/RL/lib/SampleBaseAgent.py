from .BaseAgent import BaseAgent
import pandas as pd
import numpy as np
from abc import abstractmethod

class SampleBaseAgent(BaseAgent):

    # _q = None
    def __init__(self):
        self._q = None

    def agent_init(self, agent_init_info):
        """Setup for the agent called when the experiment first starts.
        
        Args:
        agent_init_info (dict), the parameters used to initialize the agent. The dictionary contains:
        {
            num_states (int): The number of states,
            num_actions (int): The number of actions,
            epsilon (float): The epsilon parameter for exploration,
            step_size (float): The step-size,
            discount (float): The discount factor,
        }
        
        """
        super().agent_init(agent_init_info)
        # Store the parameters provided in agent_init_info.
        self.num_actions = agent_init_info["num_actions"]
        self.num_states = agent_init_info["num_states"]
        self.rand_generator = np.random.RandomState(agent_init_info["seed"])
        
        if self.is_training__:
            self.epsilon = agent_init_info["epsilon"]
            self.step_size = agent_init_info["step_size"]
            self.discount = agent_init_info["discount"]
            # Create an array for action-value estimates and initialize it to zero.
            self._q = np.zeros((self.num_states, self.num_actions)) # The array of action-value estimates.

    # q = property(q_getter, q_setter)

    # @property
    def get_q(self):
        return self._q
    
    # @q.setter
    # def q(self, value):
    #     # print('Setting q:', value)
    #     self._q__ = value

    def chose_action(self, state):
        current_q = self._q[state,:]
        action = None
        if self.is_training__:
            if self.rand_generator.rand() < self.epsilon:
                action = self.rand_generator.randint(self.num_actions)
            else:
                action = self.argmax(current_q)
        else:
            action = self.argmax(current_q)

        return action
    
    @abstractmethod
    def agent_end_update(self, reward):
        """Q Update end-of-episode ."""


    @abstractmethod
    def agent_step_update(self, reward):
        """Q Updating in-step ."""

    
    def agent_step(self, reward, observation):
        """A step taken by the agent.
        Args:
            reward (float): the reward received for taking the last action taken
            observation (int): the state observation from the
                environment's step based on where the agent ended up after the
                last step.
        Returns:
            action (int): the action the agent is taking.
        """
        
        # Choose action using epsilon greedy.
        state = observation

        action = self.chose_action(state)
        
        if self.is_training__:
            self.agent_step_update(state, reward)
        
        self.prev_state = state
        self.prev_action = action
        return action
    

    def agent_end(self, reward):
        """Run when the agent terminates.
        Args:
            reward (float): the reward the agent received for entering the
                terminal state.
        """
        if self.is_training__:
            self.agent_end_update(reward)