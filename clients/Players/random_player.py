import random
import sys
import socket
import json 
from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def Move(self, list_of_plays):
        pass 

class Random_Player(Player):
    def __init__(self):
        super().__init__()


    def Move(self, list_of_plays: list):
        r = random.randint(0, len(list_of_plays))
        return list_of_plays[r]
    
            