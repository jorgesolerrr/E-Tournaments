from abc import ABC, abstractmethod
import inspect

class IPlayer(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def Move(self, list_of_plays):
        pass 

def isIPlayer(cls):
    cls_functions = inspect.getmembers(cls, inspect.isfunction)
    iPlayer_functions = inspect.getmembers(IPlayer, inspect.isfunction)
    cls_functions = [func_name for func_name, func in cls_functions]

    for name, func in iPlayer_functions:
        if name not in cls_functions:
            return False
    return True