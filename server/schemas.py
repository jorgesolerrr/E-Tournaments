from pydantic import BaseModel

class Table_Connection(BaseModel):
    current: str
    previous : str
    next1 : str
    next2 : str

class Url(BaseModel):
    ip : str
    port : int

class Ports(BaseModel):
    ports : list[int]

class Game_Schema(BaseModel):
    amount_players : int
    name : str

class Player_Schema(BaseModel):
    id : int
    type: str
    
class Match_Schema(BaseModel):
    id : int
    tournament_name : str
    players : list[Player_Schema]
    game : Game_Schema
    game_code : str
    players_code : str

class Stats_Schema(BaseModel):
    winners : list[Player_Schema]
    score : dict
    bestPlayer : Player_Schema
    victories : list

class Tournament_State(BaseModel):
    finished : bool
    missing_matchs : list[Match_Schema]

class Tournament_data(BaseModel):
    name : str
    type : str
    game : Game_Schema
    players : list[Player_Schema]
    statistics : Stats_Schema
    state : Tournament_State


class Tournament_Schema(BaseModel):
    name : str
    type : str
    game : Game_Schema
    players : list[Player_Schema]