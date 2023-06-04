from fastapi import FastAPI, BackgroundTasks
from .schemas import Match_Schema
from Games import TicTacToe, IGame
from Players import Random_Player
from fastapi.encoders import jsonable_encoder
import uvicorn
import socket

match_server = FastAPI()

availables_games = {
    "TicTacToe": TicTacToe
}

availables_players = {
    "random" : Random_Player
}
available = True
def _playMatch(match : Match_Schema):
    
    current_game : IGame = availables_games[match.game]()
    players = []
    for player in match.players:
        players.append(availables_players[player.type]())
    
    current_game.SetState(players, players[0])
    while not current_game.GameEnd():
        count = 0
        for player in players:
            moves = current_game.GetMoves()
            current_move = player.Move(moves)
            print(f"player {count} make a move : {current_move}")
            current_game.SetMove(current_move)
            count+=1
        count = 0
    available = True

    print(f"the winners are {current_game.GetWinners()}")

@match_server.post("/play_match")
def PlayMatch(match : Match_Schema,
              background : BackgroundTasks):
    available = False
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
        response = {
            "success" : "Executing match"
        }
    except:
        available = True
        response = {
            "error": "Something went wrong during the game"
        }
    return jsonable_encoder(response)

@match_server.get("/available")
def CheckAvailable():
    response = {
        "available" : available
    }
    return jsonable_encoder(response)


if __name__ == "__main__":
    #host = socket.gethostbyname(socket.gethostname())
    uvicorn.run("match_server:match_server", host="0.0.0.0", port=8080, reload=True)
