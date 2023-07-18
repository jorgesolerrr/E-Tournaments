from abc import ABC, abstractmethod
import inspect

class IGame(ABC):
    def __init__(self):
        self.finished = False
        self.winners = None
        self.current = None

    @abstractmethod
    def SetState(self, players, current):
        pass

    @abstractmethod
    def GetMoves(self):
        pass

    @abstractmethod
    def SetMove(self, move):
        pass

    @abstractmethod
    def GameEnd(self):
        pass

    @abstractmethod
    def GetWinners(self):
        pass

def isIGame(cls):
    cls_functions = inspect.getmembers(cls, inspect.isfunction)
    iGame_functions = inspect.getmembers(IGame, inspect.isfunction)
    cls_functions = [func_name for func_name, func in cls_functions]

    for name, func in iGame_functions:
        if name not in cls_functions:
            return False
    return True
