import importlib.util
import inspect
import time
from fastapi import FastAPI, Response, BackgroundTasks,Request, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from schemas import Url, Table_Connection, Tournament_Schema, Tournament_data, Ports, Stats_Schema, Tournament_State, Player_Schema
from server_enviroment import Server_env
from Interfaces import IGame, isIGame, IPlayer, isIPlayer
import requests
import json
from tournaments import League, Playoffs
import uvicorn
import sys
from os import getcwd, listdir
import os
import socket
import logging



logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

server_routes = FastAPI()
tournaments = {}
env = Server_env()
available = True

tournaments_types = {
    "league" : League,
    "playoffs" : Playoffs
}
def Available():
    for tournament in tournaments.keys():
        if not tournaments[tournament].finished:
            return False
    return True


@server_routes.get("/Available")
def Available_route():
    return Available()

@server_routes.post("/SetEnv")
async def SetEnv(request:Request):
    data = await request.json()
    return env.set_env(data)

@server_routes.post("/create_tournament")
def create_tournament(tournament : Tournament_Schema):
    my_address = get_node_connection("current")
    if env.current_tournament != my_address: 
        return requests.post(f"http://{env.current_tournament}/create_tournament", json=jsonable_encoder(tournament)).json()
    
    games_path = getcwd() + "/games"
    players_path = getcwd() + "/players"
    if not f"{tournament.game.name}.py" in listdir(games_path):
        return JSONResponse(content={"error": f"The code of game {tournament.game.name} doesn't exist, please provide the code"}, status_code=404)

    available_players = listdir(players_path)
    for player in tournament.players:
        if f"{player.type}.py" not in available_players:
            return JSONResponse(content={"error": f"The code of player {player.id} doesn't exist, please provide the code"}, status_code=404)
    
    currentTournament = tournaments_types[tournament.type](env, name = tournament.name, game = tournament.game, type = tournament.type, players=tournament.players)
    currentTournament.AddTournamentToData()
    tournaments[tournament.name] = currentTournament
    next1 = get_node_connection("next1")
    if next1 == "":
        UpdateCurrent(my_address)
    else:
        UpdateCurrent(next1)

    return "success"

@server_routes.post("/finish_tour")
def finishTournament(tournamentData : Tournament_data):
    print("---------------->Voy A terminar: " + tournamentData.name)
    try:
        unFinishTour = tournaments_types[tournamentData.type](env,tournament_data=tournamentData)
        tournaments[tournamentData.name] = unFinishTour
        print(tournaments)
        with open("./table_connection.json") as table:
            table_json = json.load(table)
        response = requests.get(f"http://{table_json['current']}/execute/{tournamentData.name}",params = {'firstTime': False})

        with open("./table_connection.json", "w") as table:
            json.dump(table_json, table)
        print(response)
        return response
    except Exception as e:
        print("ERROR: " + str(e))

@server_routes.get("/execute/{name}")
def execute(background : BackgroundTasks,name: str, firstTime : bool):
    
    try:
        available = False 
        background.add_task(tournaments[name].Execute, firstTime)
        response = "executing in background"
    except KeyError:
        available = True
        my_addrs = get_node_connection("current")
        logger.info(f"*************{my_addrs}********")
        url_to_execute = findTournament(name)
        if url_to_execute is None:
            logger.error("No tournament found")
            return {"error": "Tournament not found"}
        return requests.get(f"http://{url_to_execute}/execute/{name}", params = {"firstTime" : firstTime}).json()

        #response = {"error": "Tournament not found"}
    except Exception as e:
        available =True
        response = {"error": str(e)}
    
    response = jsonable_encoder(response)
    return response




@server_routes.post("/addMatchServer")
def add_match_server(url : str, begin = ""):
    env.add_match_server(url)
    next = get_node_connection("next1")
    current = get_node_connection("current")
    if begin == "":
        begin = current
    
    if next == begin:
        return True
    if next == "":
        return True
    return requests.post(f"http://{next}/addMatchServer", params={"url" : url, "begin" : begin}).json()



@server_routes.post("/SetTableConnection")
def set_table_connection(url : Url):
    
    with open("./table_connection.json") as table:
        table_json = json.load(table)
    current = f"{url.ip}:{url.port}"
    table_json["current"] = current
    with open("./table_connection.json", "w") as table:
        json.dump(table_json, table)

    return "success"

@server_routes.post("/AddTourServer")
def add_server(url : str):
    with open('./table_connection.json') as table_file:
        table = json.load(table_file)
    
    if isconnect(url, table['previous']):
        with open('./table_connection.json', 'w') as table_file:
            json.dump(table, table_file)
        return 
    
    #Mi anterior es al que me quiero conectar.
    table['previous'] = url

    #Mi siguiente es el siguiente del nodo al que me quiero conectar, es decir, me pongo en el medio entre ellos.
    table['next1'] = requests.get(f'http://{url}/GetNodeConnection', params= {"position": "next1"}).json()
    print(table['next1'])
    if table['next1']:
        #El nodo al que current quiero conectar ahora tiene como 'next2' a su antiguo 'next1'.
        requests.post(f'http://{url}/Insert', params= { "position": "next2", "url" : table["next1"]})
        #Mi segundo sguiente es el correspondiente del nodo al que current quiero conectar. 
        table['next2'] = (requests.get(f'http://{table["next1"]}/GetNodeConnection', params= {"position": "next1"})).json()
    else:
        #Si table['next1'] == '' implica que te conectaste a un nodo que estaba solo, por tanto, tu próximo es él.
        table['next1'] = url

    #El nodo al que me quiero conectar ahora me tiene como su 'next1'.
    requests.post(f'http://{url}/Insert', params= { "position": "next1", "url" : table["current"]})

    #El nodo anterior al que me quiero conectar.
    prev_url = requests.get(f'http://{url}/GetNodeConnection', params= {"position": "previous"}).json()

    if prev_url:
        #El nado anterior al que current quiero conectar ahora current tiene a mi como segundo siguiente.
        requests.post(f'http://{prev_url}/Insert', params= {"position": "next2", "url" : table["current"]})
    else:
        #Si no existe el anterior al nodo al que me quiero conectar, significa que es el primer nodo de la red, por tanto, su anterior soy yo.
        requests.post(f'http://{url}/Insert', params= {"position": "previous", "url" : table["current"]})

    #El nodo siguiente al que le pedí conexión ahora me tiene como su anterior.
    requests.post(f'http://{table["next1"]}/Insert', params= {"position": "previous", "url" : table["current"]})
    
    with open('./table_connection.json', 'w') as table_file:
        json.dump(table, table_file)   
    
    #actualizo el lider
    leader = requests.get(f"http://{url}/GetLeader").json()
    env.leader = leader
    current = requests.get(f"http://{url}/GetCurrentT").json()
    env.current_tournament = current
    matches = requests.get(f"http://{url}/GetMatches").json()
    env.match_servers = [tuple(url) for url in matches]
    logger.info("VOY A TRAER EL CODIGO QUE EXISTA")
    available_code = requests.get(f"http://{leader}/GetAvailableCode").json()
    for game in available_code["games"]:
        if ".py" not in game:
            continue
        logger.info("VOY A DESCARGAR EL ARCHIVO : " + game)
        response = requests.get(f"http://{leader}/DownloadCode", params={"filename" : game, "game" : True})
        with open("./games/" + game, "wb") as game_file:
            game_file.write(response.content)
            game_file.close()
    logger.info("TERMINE DE DESCARGAR LOS JUEGOS, REVISA SI QUIERES")
    for player in available_code["players"]:
        if ".py" not in player:
            continue
        logger.info("VOY A DESCARGAR EL ARCHIVO : " + player)
        response = requests.get(f"http://{leader}/DownloadCode", params={"filename" : player, "game" : False})
        with open("./players/" + player, "wb") as player_file:
            player_file.write(response.content)
            player_file.close()
    
    logger.info("TERMINE DE DESCARGAR TODO")


    #voy a replicar el table propio de mi antecesor
    update_data()
    #mi sucesor va a replicar mi información, la cual es necesariamente vacia y por ende se manda a limpiar su table replicado
    requests.post(f'http://{table["next1"]}/UpdateData', params={"clean": True})
    

    return "success"

@server_routes.get("/GetCurrentT")
def get_current_T():
    return env.current_tournament

@server_routes.get("/DownloadCode")
def download_code(filename : str, game : bool = True):
    if game:
        path = "./games"
    else:
        path = "./players"
    
    if filename not in listdir(path):
        return False
    
    return FileResponse(f"{path}/{filename}", filename=filename)


@server_routes.get("/GetAvailableCode")
def getAvailableCode():
    path_games = "./games"
    path_players = "./players"
    
    code = {
        "games" : listdir(path_games),
        "players" : listdir(path_players)
    }
    return jsonable_encoder(code)


@server_routes.get("/GetNodeConnection")
def get_node_connection(position: str):
    with open('./table_connection.json') as table_file:
        table = json.load(table_file)
        table_file.close()
    aux = table[position]
    print(aux)
    with open('./table_connection.json', 'w') as table_file:
        json.dump(table, table_file)
    return aux

@server_routes.post("/Insert")
def insert(position: str, url: str):    
    with open('./table_connection.json') as table_file:
        table = json.load(table_file)
    table[position] = url
    print(table)
    with open('./table_connection.json', 'w') as table_file:
        json.dump(table, table_file)

@server_routes.get("/GetLeader")
def getLeader():
    return env.leader

@server_routes.get("/IsConnect")
def isconnect(url_to_search: str, who_asks):
    with open('./table_connection.json') as table_file:
        table = json.load(table_file)

    #si me buscan a mí o a mi sucesor digo que sí
    if url_to_search == table['current'] or url_to_search == table['next1']:
        with open('./table_connection.json', 'w') as table_file:
            json.dump(table, table_file)
        return True

    if table["previous"] == table["next1"] == table["next2"] == "":
        return False
    #si yo o mi sucesor somos los que preguntamos, digo que no
    elif who_asks == table['current'] or who_asks == table['next1']:
        with open('./table_connection.json', 'w') as table_file:
            json.dump(table, table_file)
        return False
    #me muevo a mi next2
    next = table['next2']
    with open('./table_connection.json', 'w') as table_file:
        json.dump(table, table_file)
    #current busco en el endpoint de este método en mi next2
    return (requests.get(f'http://{next}/IsConnect', params= {"url_to_search": url_to_search, "who_asks": who_asks})).json()


@server_routes.post("/SendGamePlayersCode")
def send_game_players(url_to_send : str):
    path_games = "./games"
    path_players = "./players"

    for game in listdir(path_games):
        try:
            response = requests.post(f"http://{url_to_send}/UploadCode", files={"file":  open(path_games + f"/{game}", "rb")}, params = {"begins" : "", "game" : True, "all" : False}).json()
        except Exception as e:
            logger.error(f"No pude subir el archivo {game} a {url_to_send} -----> {str(e)}")
        if not response or "error" in response.keys():
            logger.error(f"No pude subir el archivo {game} a {url_to_send}")

    for player in listdir(path_players):
        try:
            response = requests.post(f"http://{url_to_send}/UploadCode", files={"file":  open(path_players + f"/{player}", "rb")}, params = {"begins" : "", "game" : False, "all" : False}).json()
        except Exception as e:
            logger.error(f"No pude subir el archivo {player} a {url_to_send} -----> {str(e)}")
        if not response or "error" in response.keys():
            logger.error(f"No pude subir el archivo {player} a {url_to_send}")
        
    return "finished"



@server_routes.get("/GetServerData")
def get_server_data(replicated: bool):
    response = None
    if not replicated:
        with open('./current_tour_data.json') as cdata_file:
            c_data = json.load(cdata_file)
        with open('./current_tour_data.json', 'w') as cdata_file:
            json.dump(c_data, cdata_file)
        response = c_data
    else:
        with open('./replicated_data.json') as rdata_file:
            r_data = json.load(rdata_file)
        with open('./replicated_data.json', 'w') as rdata_file:
            json.dump(r_data, rdata_file)
        response = r_data
    return response

#Replicar información
@server_routes.post("/UpdateData")
def update_data(clean=False):
    with open('./replicated_data.json') as rdata_file:
        r_data = json.load(rdata_file)
    with open('./table_connection.json') as table_file:
        table = json.load(table_file)
    previous = table["previous"]
    with open('./table_connection.json', 'w') as table_file:
        json.dump(table, table_file)
    if clean:
    #se limpia la información replicada que guarda este servidor
        r_data = {
            "next_tournament" : "",
            "tournaments": []
        }
    else:
        #se obtiene el data propio de mi antecesor, el cual debo replicar en mi
        prev_data = requests.get(f'http://{previous}/GetServerData', params= {"replicated": False}).json()  
        #se añade a mi información replicada la información propia de mi antecesor
        r_data["next_tournament"] = ""
        for tourn in prev_data["tournaments"]:
            if len(r_data["tournaments"]) == 0:
                r_data["tournaments"].append(jsonable_encoder(tourn))
                continue
            for i in range(len(r_data["tournaments"])):
                if r_data["tournaments"][i]["name"] == tourn["name"]:
                    t = r_data["tournaments"].pop(i)
                    r_data["tournaments"].append(jsonable_encoder(tourn))
                    break
                    
    with open('./replicated_data.json', 'w') as rdata_file:
        json.dump(r_data, rdata_file)
    return 

@server_routes.get("/Ping")
def ping(server):    
    try:
        requests.get(f'http://{server}/Active', timeout=10)
        return 200
    except:
        return 500

@server_routes.post("/UpdateLeader")
def UpdateLeader(url : str):
    env.set_leader(url)
    with open('./table_connection.json') as table_file:
        table = json.load(table_file)
        table_file.close()
    
    if table["next1"] == url:
        return True

    return requests.post(f"http://{table['next1']}/UpdateLeader", params={"url": url}).json()

@server_routes.post("/UpdateCurrent")
def UpdateCurrent(url : str, begin: str = ""):
    env.set_current_tournament(url)
    with open('./table_connection.json') as table_file:
        table = json.load(table_file)
        table_file.close()
    
    if begin == "":
        begin = table["current"]

    if table["next1"] == "":
        return True

    if table["next1"] == begin:
        return True

    return requests.post(f"http://{table['next1']}/UpdateCurrent", params={"url": url, "begin" : begin}).json()

@server_routes.get("/Active")
def active():
  return True  

def check_forUnfinishedTour():
    print("ESTOY CHECKEANDO SI HAY TORNEOS SIN TERMINAR")
    with open('./current_tour_data.json') as cdata_file:
        current_data = json.load(cdata_file)
        cdata_file.close()
    
    for tour in current_data["tournaments"]:
        if tour["name"] in tournaments.keys():
            continue
        print(tour["state"]["finished"])
        print(f"*********************PARTIDAS QUE QUEDAN DE : {tour['name']}********************************")
        print(tour["state"]["missing_matchs"])

        if not tour["state"]["finished"]:
            tournament_data = Tournament_data( 
                                                name=tour["name"], type=tour["type"], 
                                                game= tour["game"], players=tour["players"],
                                                statistics=Stats_Schema(winners=tour["statistics"]["winners"], score=tour["statistics"]["score"],
                                                                       bestPlayer=Player_Schema(id=tour["statistics"]["bestPlayer"]["id"], 
                                                                                                type= tour["statistics"]["bestPlayer"]["type"]), victories=tour["statistics"]["victories"]),
                                                state=Tournament_State(finished=tour["state"]["finished"], missing_matchs=tour["state"]["missing_matchs"])    
                                            ) 
            print("***********DATA QUE HAY EN EL TORNEO QUE NO HA TERMINADO*********************")
            print(dict(tournament_data))
            finishTournament(tournament_data)
            return tournament_data.name
    # with open('./current_tour_data.json', "w") as cdata_file:
    #     json.dump(current_data, cdata_file)

def finish_already_run_Tour(name):
    with open('./current_tour_data.json') as cdata_file:
        current_data = json.load(cdata_file)
        cdata_file.close()
    for tour in current_data["tournaments"]:
        if (tour["name"] != name) and (not tour["state"]["finished"]):
            tournament_data = Tournament_data( 
                                                name=tour["name"], type=tour["type"], 
                                                game= tour["game"], players=tour["players"],
                                                statistics=Stats_Schema(winners=tour["statistics"]["winners"], score=tour["statistics"]["score"],
                                                                       bestPlayer=Player_Schema(id=tour["statistics"]["bestPlayer"]["id"], 
                                                                                                type= tour["statistics"]["bestPlayer"]["type"]), victories=tour["statistics"]["victories"]),
                                                state=Tournament_State(finished=tour["state"]["finished"], missing_matchs=tour["state"]["missing_matchs"])    
                                            )
            finishTournament(tournament_data)
            


@server_routes.on_event('startup')
@repeat_every(seconds=10)
def check():
  with open('./table_connection.json') as table_file:
    table = json.load(table_file)
    table_file.close()
    #si no puedo llegar a mi next1 desconectalo de la red
    if table["next1"] and ping(table["next1"]) == 500:
        todisc = table["next1"]
        print("Voy a desconectar a: " + table["next1"])
        disconnect(table)
        if env.leader == todisc:
            resp = UpdateLeader(table["current"])
            logger.info("HAY UN NUEVO LIDER : ----->" + table["current"])
        if env.current_tournament == todisc:
            if table["next1"] == "":
                UpdateCurrent(table["current"])
            else:
                UpdateCurrent(table["next1"])

        name = check_forUnfinishedTour()
        print("TORNEO QUE ESTOY TERMINANDO DE OTRO SERVIDOR: " + name)
        finish_already_run_Tour(name)
        

  with open('./table_connection.json', 'w') as table_file:
    json.dump(table, table_file)

@server_routes.get("/FindTournament")
def findTournament(tour_name: str, who_asks: str =  ""):
    me = get_node_connection("current")
    logger.info(f"***********entre a un servidor a buscar el torneo {me}*********")
    with open('./current_tour_data.json') as cdata_file:
        current_data = json.load(cdata_file)
    # with open('./table_connection.json') as table_file:
    #     table = json.load(table_file)
    tournaments = current_data['tournaments']
    #revisar si algun usuario de los registrados en este servidor es el que busco
    for tourn in tournaments:
        if tour_name == tourn['name']:
        #si lo encuentro cierro los json y lo devuelvo
            # with open('./table_connection.json', 'w') as table_file:
            #     json.dump(table, table_file)
            with open('./current_tour_data.json', 'w') as cdata_file:
                json.dump(current_data, cdata_file)

            return str(get_node_connection("current"))
    
    if who_asks == "":
        who_asks = me
    #si vuelvo a la persona que pregunta devuelvo None
    # not who_asks or  
    if who_asks == get_node_connection("next1"):
        # with open('./table_connection.json', 'w') as table_file:
        #     json.dump(table, table_file)
        with open('./current_tour_data.json', 'w') as cdata_file:
            json.dump(current_data, cdata_file)
        
        return None
    # with open('./table_connection.json', 'w') as table_file:
    #     json.dump(table, table_file)
    with open('./current_tour_data.json', 'w') as cdata_file:
        json.dump(current_data, cdata_file)
    #sigo buscando preguntándole a mi sucesor
    loc = str(get_node_connection("next1"))
    return requests.get(f'http://{loc}/FindTournament', params= {"tour_name": tour_name, "who_asks": who_asks}).json()


def disconnect(table):
    try:
        print("ESTOY DESCONECTANDO")
        #Mi 'next_1' ahora es mi 'next_2'.
        table['next1'] = table['next2'] 
        if table["next2"]:
            #Para desconectar a 'next_1' el anterior a mi 'next_2' ahora soy yo.
            print("ESTOY BUSCANDO MI NEXT2")
            requests.post(f'http://{table["next2"]}/Insert', params= {"position": "previous", "url" : table["current"]})  
            #Mi 'next_2' será el 'next_1' de mi antiguo 'next_2'.
            table['next2'] = requests.get(f'http://{table["next2"]}/GetNodeConnection', params= {"position": "next1"}).json()
            #caso especial: si eramos 3 servidores y ahora somos 2 tengo que limpiar mi segundo predecesor
            if table['next2'] == table["current"]:
                table['next2'] = ""
        
        print("ESTOY TRATANDO DE HACER PING CON MI PREV")
        if table['previous'] and ping(table["previous"]) == 200:
            if table['previous'] == table['next1']:
            #solo quedamos 2, actualizar el otro nodo limpiando su next2
                requests.post(f'http://{table["previous"]}/Insert', params= {"position": "next2", "url" : ""}) 
            else:
            #Actualizar el anterior a mi con su 'next_2' igual a mi nuevo 'next_1'.
                requests.post('http://'+table["previous"]+'/Insert', params= {"position": "next2", "url" : table["next1"]}) 

            #me quedo con el data replicado de mi sucesor
            replicated_data = requests.get(f'http://{table["next1"]}/GetServerData', params= {"replicated": True}).json()      
            print(replicated_data)
            #mi sucesor añade mi data propio a su data replicado
            requests.post(f'http://{table["next1"]}/UpdateData') 
            with open('./current_tour_data.json') as cdata_file:
                c_data = json.load(cdata_file)
            #añado a mi data propio el data replicado que tiene mi sucesor y yo no tengo 
            for tourn in replicated_data["tournaments"]:
                c_data["tournaments"].append(tourn)
            with open('./current_tour_data.json', 'w') as cdata_file:
                json.dump(c_data, cdata_file)    
        else:
            table['previous'] = ""
            with open('./current_tour_data.json') as cdata_file:
                c_data = json.load(cdata_file)
            with open('./replicated_data.json') as rdata_file:
                r_data = json.load(rdata_file)
            for tourn in r_data["tournaments"]:
                c_data["tournaments"].append(tourn)
            r_data = {"tournaments":[]}
            with open('./current_tour_data.json', 'w') as cdata_file:
                json.dump(c_data, cdata_file)
            with open('./replicated_data.json', 'w') as rdata_file:
                json.dump(r_data, rdata_file)

        print("ESTOY ACTUALIZANDO LAS CONEXIONES")
        with open('./table_connection.json', 'w') as table_file:
            json.dump(table, table_file)
        # resp = UpdateLeader(table["current"])
    except Exception as e:
        print("***************ERROR : " + str(e))

@server_routes.get("/FindAvailableServer")
def find_available_server():
    with open('./table_connection.json') as table_file:
        table = json.load(table_file)
    if Available():
        with open('./table_connection.json', 'w') as table_file:
            json.dump(table, table_file)
        return table["current"]
    else:
        with open('./table_connection.json', 'w') as table_file:
            json.dump(table, table_file)
        if table["next1"]:
            return requests.get(f"http://{table['next1']}/FindAvailableServer").json()
        else:
            return ""

@server_routes.get("/GetMatches")
def getMatches():
    return env.match_servers


@server_routes.post("/UploadCode")
async def Upload_game(file : UploadFile = File(...), begins : str = "", game : bool = True, all : bool = True):
    logger.info("***************ENTRE A SUBIR UN .py")
    #! quitar server del path
    path = ""
    if game:
        path = "./games"
    else:
        path = "./players"
    next = get_node_connection("next1")
    current = get_node_connection("current")

    if len(begins) == 0:
        begins = current

    content = await file.read()
    if not file.filename in listdir(path):   
        with open(path + f"/{file.filename}","wb") as pyFile:
            logger.info("***************ESTOY GUARDANDO EL ARCHIVO")
            pyFile.write(content)
            pyFile.close()
    
    if begins == current:
        new_module_path = path + f"/{file.filename}"
        module_name = file.filename.split(".")[0]
        spec = importlib.util.spec_from_file_location(module_name, new_module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module_class = inspect.getmembers(module, inspect.isclass)
        find_class = False
        for class_name, cls in module_class:
            if game and isIGame(cls):
                if class_name == module_name:
                    find_class = True
                    break
                else:
                    return JSONResponse(content={"error" : "La clase que implementa el juego debe tener el mismo nombre que el modulo"}, status_code=400)
            elif (not game) and isIPlayer(cls):
                if class_name == module_name:
                    find_class = True
                    break
                else:
                    return JSONResponse(content={"error" : "La clase que implementa el jugador debe tener el mismo nombre que el modulo"}, status_code=400)
        if not find_class:
            return JSONResponse(content={"error" : "En el módulo que se mandó no hay ninguna clase que implemente la interfaz requerida"}, status_code=400)

    if begins == next:
        return True
    
    if len(next) == 0:
        return True
    logger.info("***************SE LO VOY A MANDAR A---------> " + next)
    try:
        response = True
        if all:
            response = requests.post(f"http://{next}/UploadCode", files={"file":  open(path + f"/{file.filename}","rb")}, params = {"begins" : begins, "game" : game, "all" : all}).json()
    except Exception as e:
        logger.error("ERROR ENVIANDO EL ARCHIVO A: " + next + "----> " + str(e))
    return response

@server_routes.on_event("startup")
def present_yourself():
    logger.info("******************ME PRESENTO***************")
    my_adress = get_node_connection("current")
    logger.info(f"el puerto por el que estoy expuesto es {my_adress}")


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


    listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        listen.bind(('', 50000))
    except Exception as e:
        logger.error(f"NO PUDE HACER BIND ----> {str(e)}")
        return present_yourself()

    mensaje = f"Hola a todos soy,{my_adress}"
    retries = 10
    count = 0
    while count <= retries: 
        sock.sendto(mensaje.encode(), ('<broadcast>', 12345))
        listen.settimeout(6)
        try:
            logger.info("**********ESPERANDO RESPUESTA DEL LIDER*******")
            msg, direccion = listen.recvfrom(1024)
            msg = msg.decode()
            logger.info(f"*************EL LÍDER RESPONDIÓ {msg}*********")
            add_server(msg)
            sock.close()
            listen.close()
            return
        except Exception as e:
            count = count + 1
    
    logger.info("*********SOY EL LÍDER*********")
    env.set_leader(my_adress)
    env.set_current_tournament(my_adress)
    listen.close()
    sock.close()

@server_routes.on_event("startup")
@repeat_every(seconds = 5)
def LookForMatches():
    my_adress = get_node_connection("current")
    #en caso de que no seas el lider no escuches
    # if env.leader == "":
    #     env.set_leader(my_adress)
    #     return
    if env.leader != my_adress:
        return
    logger.info("**************LíDER BUSCANDO PARTIDAS***********")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    talker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    talker.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.bind(('', 60000))
    except Exception as e:
        logger.error("NO PUDE HACER BIND : " + str(e))
        sock.close()
        return
    try:
        sock.settimeout(4)
        mensaje, direccion = sock.recvfrom(1024)
        mensaje = mensaje.decode()
        logger.info(mensaje)
        address = mensaje.split(",")[1]
        logger.info(f"****NUEVO SERVIDOR DE PARTIDAS -> {address}*****")
        add_match_server(address,"")
        try:
            talker.sendto(address.encode(), ('<broadcast>', 50400))
            logger.info(f"***********RESPUESTA ENVIADA AL SERVIDOR DE PARTIDAS ->{address}**************")
        except Exception as e:
            logger.info(f"**********{str(e)}****************")
        
    except Exception as e:
        logger.info( f"**********{str(e)}************")
    sock.close()
    talker.close()
        

# @server_routes.on_event("startup")
# def NoLeader():
#     time.sleep(8)
#     logger.info(f"*************{e}********")
#     logger.info("*********SOY EL LÍDER*********")
#     env.set_leader(my_adress)
#     listen.close()
# @server_routes.on_event("startup")
# def WaitForLeader():
#     my_adress = get_node_connection("current")
#     logger.info("**********ESPERANDO RESPUESTA DEL LIDER*******")
#     listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     listen.bind(('', 50000))
#     try:
#         msg, direccion = sock.recvfrom(1024)
#         msg = mensaje.decode()
#         logger.info(f"*************EL LÍDER RESPONDIÓ {msg}*********")
#         add_server(msg)
#     except Exception as e:
#         logger.info(f"*************{e}********")
#         logger.info("*********SOY EL LÍDER*********")
#         env.set_leader(my_adress)
#     listen.close()


@server_routes.on_event("startup")
@repeat_every(seconds = 5)
def Listen():
    my_adress = get_node_connection("current")
    #en caso de que no seas el lider no escuches
    # if env.leader == "":
    #     env.set_leader(my_adress)
    #     return
    if env.leader != my_adress:
        return

    logger.info("**************ESTOY ESCUCHANDO***********")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    talker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    talker.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.bind(('', 12345))
    except Exception as e:
        logger.error("NO PUDE HACER BIND : " + str(e))
        sock.close()
        return
    #logger.info("LOGRE HACER BIND")
    try:
        sock.settimeout(4)
        mensaje, direccion = sock.recvfrom(1024)
        logger.info("*****RECIBI UN MENSAJE*****")
        mensaje = mensaje.decode()


        if mensaje == "Aceptado":
            logger.info("ACEPTADO")
            sock.close()
            return
        if mensaje == "No Aceptado":
            logger.info("NO ACEPTADO")
            present_yourself()
        if "Hola a todos" in mensaje:
            logger.info(mensaje)
            address = mensaje.split(",")[1]
            matches = getMatches()
            #añadiendo servidor al anillo
            try:
               
                msg = env.leader
                talker.sendto(msg.encode(), ('<broadcast>', 50000))
                
            except Exception as e:
                logger.error(f"NO PUDE AÑADIR A : {address} AL ANILLO -----> {str(e)}")
                back_message = b"No Aceptado"
    except:
        sock.close()
        talker.close()
        return
        #sock.sendto(back_message, direccion)
    #caso en que esté yo solo en la red, no sé si es que el tipo recibe mensaje vacío
    # if mensaje == "":
    #     if env.leader == "":
    #         env.set_leader(my_adress)
    
    sock.close()
    talker.close()
            

@server_routes.get("/GetTournamentData")
def get_tournament_data(tour_name:str, who_asks:str):
    data = requests.get(f"http://{who_asks}/GetServerData",params={"replicated":False})

    try:
        return data
    except:
        return Exception("No tournament name like " + tour_name)    

server_routes.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    
    

if __name__ == "__main__":
    try: 
        arg1 = int(sys.argv[1])
    except:
        arg1 = 5010

    host = socket.gethostbyname(socket.gethostname())
    logger.info("SOY: " + host)
    set_table_connection(Url(ip=host, port=arg1))
    uvicorn.run("server_routes:server_routes", host="0.0.0.0", port=arg1, reload=False)
    print("hola")