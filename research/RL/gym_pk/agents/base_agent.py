from gymnasium.spaces import Space

class BaseAgent():

    def __init__(self, action_space: Space) -> None:
        self.action_space = action_space
        
    def initialize(**agent_params):
        pass

    def start_episode(self):
        pass


    def get_episode_history(self):
        pass

    def get_info():
        raise "Not Implemented."