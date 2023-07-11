from fastapi import FastAPI, BackgroundTasks
from schemas import Match_Schema
from Games import TicTacToe, IGame
from Players import Random_Player
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import uvicorn
import socket
import sys

match_server = FastAPI()

availables_games = {
    "TicTacToe": TicTacToe
}

availables_players = {
    "random" : Random_Player
}
executed_matches = {}


available = True

def _playMatch(match : Match_Schema):
    
    current_game : IGame = availables_games[match.game.name]()
    players = []
    for player in match.players:
        players.append((availables_players[player.type](), player.id))
    
    current_game.SetState(players, players[0][0])
    while not current_game.GameEnd():
        count = 0
        for player in players:
            moves = current_game.GetMoves()
            if len(moves) == 0:
                current_game.winners = [player[1] for player in players]
                break
            current_move = player[0].Move(moves)
            print(f"player {player[1]} make a move : {current_move}")
            current_game.SetMove(current_move)
            count+=1
        count = 0
    executed_matches[match.tournament_name][match.id] = current_game.GetWinners()

    available = True

    print(f"the winners are {current_game.GetWinners()}")

@match_server.post("/play_match")
def PlayMatch(match : Match_Schema,
              background : BackgroundTasks):
    available = False
    try:
        aux = executed_matches[match.tournament_name]
    except KeyError:
        executed_matches[match.tournament_name] = {}
        
    if not (match.game.name in availables_games):
        response = {
            "error": "This game is not available"
        }
        available = False
        return jsonable_encoder(response)
    for player in match.players:
        if not (player.type in availables_players):
            response = {
                "error": "This game is not available"
            }
            return jsonable_encoder(response)
    try:
        background.add_task(_playMatch, match)
        print(f"Ejecutando partida : {match.id}")
        response = {
            "success" : "Executing match"
        }
    except:
        available = True
        response = {
            "error": "Something went wrong during the game"
        }
    return jsonable_encoder(response)

@match_server.get("/active")
def Check():
    return True



@match_server.get("/winners/{tournament}/{matchid}")
def CheckWinners(tournament : str,matchid : int):
    try:
        response = executed_matches[tournament][matchid]
    except KeyError:
        response = []

    return jsonable_encoder(response)

@match_server.get("/executed_matches/{tournament}")
def get_executed_matches(tournament: str):
    try:
        response = executed_matches[tournament]
    except KeyError:
        response = {}

    return jsonable_encoder(response)


match_server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    #host = socket.gethostbyname(socket.gethostname())
    try: 
        arg1 = int(sys.argv[1])
    except:
        arg1 = 5020
    uvicorn.run("match_server:match_server", host="0.0.0.0", port=arg1, reload=True)
