from abc import ABC, abstractmethod

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