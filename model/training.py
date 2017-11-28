from collections import namedtuple, deque
from torch.autograd import Variable
import torch

import ActionGenerator


State = namedtuple('State', ['image', 'mission', 'advice'])

Trans = namedtuple('Trans', ['state', 'action', 'nextState', 'reward'])

model=ActionGenerator.ActionGenerator()


def selectAction(state):
    """
    Select the next action to be performed in an episode
    @state tuple containing (image, mission, advice)
    """

    # TODO
    print('selectAction: implement me!')
    
    
    #pre processing
    advice=model.processText(state.advice)
    
    
    print(type(advice))
    
    
    
    
    
    import random
    return random.randint(0, 3)
