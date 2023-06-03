from pydantic import BaseModel

class Game_Schema(BaseModel):
    amount_players : int
    name : str

class Match_Schema(BaseModel):
    players : list
    game : Game_Schema

class Player_Schema(BaseModel):
    id : int
    type: str

class Tournament_Schema(BaseModel):
    name : str
    type : str
    game : Game_Schema
    players : list[Player_Schema]