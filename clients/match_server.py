from fastapi import FastAPI, BackgroundTasks
from schemas import Match_Schema
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import uvicorn
import socket 
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


match_server = FastAPI()
match_server.port =str(sys.argv[1])

executed_matches = {}


available = True

def _playMatch(match : Match_Schema):
    try: 
        exec(match.game_code)
    except Exception as e:
        logger.error(f"Error ejecutando el codigo de {match.game.name} ---> {str(e)}")
        return
    
    for player_code in match.players_code:
        try: 
            exec(player_code)
        except Exception as e:
            logger.error(f"Error ejecutando el codigo de uno de los Players ---> {str(e)}")
            return
    
    local_vars = locals()
    try :
        current_game = local_vars[match.game.name]
    except KeyError:
        logger.error("El nombre de la clase debe coincidir con el nombre del juego")
        return
    
    availables_players = {}
    for player in match.players:
        try:
            availables_players[player.type] = local_vars[player.type]
        except KeyError:
            logger.error("El nombre de la clase debe coincidir con el tipo de jugador")
            return
    


    current_game  = type(current_game).__call__(current_game)
    players = []
    for player in match.players:
        players.append((type(availables_players[player.type]).__call__(availables_players[player.type]), player.id))
    
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



@match_server.on_event("startup")
def Login():
    logger.info("**************LíDER BUSCANDO PARTIDAS***********")
    log = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    host = socket.gethostbyname(socket.gethostname())
    port = match_server.port
    while(True):
        lis = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = f"Hola a todos,{host}:{port}"
        logger.info(msg)
        log.sendto(msg.encode(), ('<broadcast>', 60000))
        try:
            
            lis.bind(('', 50400))
        except Exception as e:
            logger.info(f"*****PUERTO POSIBLEMENTE OCUPADO*************{str(e)}*************")
            lis.close()
            continue
        try:
            lis.settimeout(8)
            mensaje, direccion = lis.recvfrom(1024)
            mensaje = mensaje.decode()
            logger.info(mensaje)
            if mensaje == f"{host}:{port}":
                break
        except Exception as e:
            logger.info( f"**********{str(e)}************")
        lis.close()
    log.close()
    

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
        match_server.port = arg1
    except:
        arg1 = 5020
        match_server.port = 5020
    uvicorn.run("match_server:match_server", host="0.0.0.0", port=arg1, reload=True)
