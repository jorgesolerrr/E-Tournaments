from pydantic import BaseModel

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
    players_code : list[str]


class Tournament_Schema(BaseModel):
    name : str
    type : str
    game : Game_Schema
    players : list[Player_Schema]