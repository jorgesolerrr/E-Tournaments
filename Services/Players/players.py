import random
from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def Move(self, list_of_plays):
        pass 

class Random_Player(Player):
    def __init__(self, name):
        super().__init__(name)


    def Move(self, list_of_plays: list):
        r = random.randint(0, len(list_of_plays))
        return list_of_plays[r]
    

class Greedy_Player(Player):
    def __init__(self, name):
        super().__init__(name)
    
    def Move(self, list_of_plays):
        return super().Move(list_of_plays) # TODO
