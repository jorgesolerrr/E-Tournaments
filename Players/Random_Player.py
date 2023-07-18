import random


class Random_Player:
    def __init__(self):
        super().__init__()


    def Move(self, list_of_plays: list):
        r = random.choice(list_of_plays)
        return r
    
            