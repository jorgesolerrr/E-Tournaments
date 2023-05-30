from fastapi import APIRouter
from tools import Tournament_Schema
from Tournaments import League

server = APIRouter()

@server.post("/create_tournament")
def create_tournament(tournament : Tournament_Schema):
    tournaments_types = {
        "league" : League
    }   

    currentTournament = tournaments_types[tournament.type](tournament.name, tournament.type, tournament.players)
    