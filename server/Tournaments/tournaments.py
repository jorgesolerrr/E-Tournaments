from abc import ABC, abstractmethod
from tools import Match_Schema, Player_Schema, Game_Schema
from itertools import combinations
import socket
import docker 


class Tournament(ABC):
    def __init__(self, name, game : Game_Schema, type, players : list):
        self.name = name
        self.game = game
        self.type = type
        self.players = players
        self.matches = []
        self.match_servers = []

    @abstractmethod
    def CreateMatches(self):
        pass

    @abstractmethod
    def GetState(self):
        pass

    def CreateTournamentEnv(self):
        

class League(Tournament):
    def __init__(self, name, type, players):
        Tournament.__init__(self, name, type, players)
        self.CreateMatches()

    def CreateMatches(self):
        match_players = combinations(self.players, self.game.amount_players)
        
        for current_players in match_players:
            self.matches.append(Match_Schema(players=list(current_players), game=self.game))
             
    