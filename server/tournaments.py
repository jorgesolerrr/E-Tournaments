from abc import ABC, abstractmethod
from schemas import Match_Schema, Player_Schema, Game_Schema, Tournament_data, Tournament_State, Stats_Schema
from itertools import combinations
from server_enviroment import Server_env
from fastapi.encoders import jsonable_encoder
import requests
import socket
import json
import docker 
import time
import random


class Tournament(ABC):
    def __init__(self, env : Server_env, name = "", game : Game_Schema = None, type = "", players : list = [], tournament_data : Tournament_data = None):
        if tournament_data is None:
            self.name = name
            self.game = game
            self.type = type
            self.players = players
            self.score = {player.id : 0 for player in players}
            self.matches = []
            self.finished = False
            self.tournament_data = Tournament_data( 
                                                name=name, type=type, 
                                                game= game, players=players,
                                                statistics=Stats_Schema(winners=[], score=self.score,
                                                                       bestPlayer=Player_Schema(id=-1, type=""), victories=[]),
                                                state=Tournament_State(finished=False, missing_matchs=self.matches)    
                                            ) 
        else:
            self.name = tournament_data.name
            self.game = tournament_data.game
            self.type = tournament_data.type
            self.players = tournament_data.players
            self.score = {player.id : 0 for player in self.players}
            self.matches = tournament_data.state.missing_matchs
            self.tournament_data = tournament_data

        self.env = env
    @abstractmethod
    def CreateMatches(self):
        pass
    
    @abstractmethod
    def Execute(self):
        pass

    @abstractmethod
    def process_score(self, winners, end = False):
        pass

    @abstractmethod
    def setWinner(self):
        pass

    def sendData(self):
        with open("./table_connection.json") as table_file:
            data_json = json.load(table_file)
        response = requests.post(f"http://{data_json['next1']}/UpdateData")
        with open("./table_connection.json", "w") as table_file:
            json.dump(data_json, table_file)

    def UpdateCurrentData(self):
        with open("./current_tour_data.json") as cdata_file:
            data_json = json.load(cdata_file)
        for i in range(len(data_json["tournaments"])):
            if data_json["tournaments"][i]["name"] == self.name:
                data_json["tournaments"].pop(i)
                tour_data = jsonable_encoder(self.tournament_data)
                data_json["tournaments"].append(tour_data)
                print("**************DATA*********************")
                print(dict(self.tournament_data))
                print("***************************************")
                break
        self.sendData()
        with open("./current_tour_data.json", "w") as cdata_file:
            json.dump(data_json, cdata_file)


class League(Tournament):
    def __init__(self, env : Server_env, name = "", game : Game_Schema = None, type = "", players : list = [], tournament_data : Tournament_data = None):
        Tournament.__init__(self, env,name= name, game=game, type=type, players=players, tournament_data=tournament_data)
        self.CreateMatches()
        self.tournament_data.state.missing_matchs = self.matches
        self.player_status = { player.id : False for player in self.players }
        self.executed_matches = {}

    def process_score(self, winners, end = False):
        executed = False
        for match in winners.keys():
            if not end:
                for exec_match in self.executed_matches.values():
                    if exec_match.id == match:
                        executed = True
            if executed:
                continue
            for player in winners[match]:
                self.score[player] += 3

        self.tournament_data.statistics.score = self.score

    def setWinner(self):
        max = 0
        winner = None
        for player in self.score.keys():
            if self.score[player] > max:
                winner = player
                max = self.score[player]
        
        for player in self.players:
            if player.id == winner:
                self.tournament_data.statistics.winners = [player]
                self.tournament_data.statistics.bestPlayer = player
                self.tournament_data.state.finished = True
                self.UpdateCurrentData()
                break

    def CreateMatches(self):
        match_players = combinations(self.players, self.game.amount_players)
        count = 0
        for current_players in match_players:
            self.matches.append(Match_Schema(id=count, tournament_name=self.name, players=list(current_players), game=self.game))
            count+=1

    def SetPlayerStatus(self, match, status):
        for player in match.players:
            self.player_status[player.id] = status

    def _checkAvailablePlayers(self, match):
        for player in match.players:
            if self.player_status[player.id]:
                return False
        return True

    def Execute(self, firstTime = True):
        if firstTime:
            with open("./current_tour_data.json") as cdata_file:
                data_json = json.load(cdata_file)
            tour_data = jsonable_encoder(self.tournament_data)
            data_json["tournaments"].append(tour_data)
            self.sendData()
            with open("./current_tour_data.json", "w") as cdata_file:
                json.dump(data_json, cdata_file)

        client = docker.from_env()
        count = 0
        while len(self.matches) > 0:
            for match_server in self.env.match_servers:
                try:
                    response = requests.get(f"http://{match_server[0]}:{match_server[1]}/available").json()
                    print(response)
                except:
                    #el servidor de partidas fallo por alguna razon
                    self.env.add_match_server(match_server[1])
                    continue

                if response["available"]:
                    if match_server[0] in self.executed_matches.keys():
                        winners = requests.get(f"http://{match_server[0]}:{match_server[1]}/winners/{self.name}").json()
                        print("************WINNERSSSS**************")
                        print(winners)
                        print("************************************")
                        # self.process_score(winners)
                        # print("**********SCORE*****************")
                        # print(self.score)
                        # print("********************************")
                        executed_match = self.executed_matches[match_server[0]]
                        self.SetPlayerStatus(executed_match, False)
                    match = None
                    for i in range(len(self.matches)):
                        if self._checkAvailablePlayers(self.matches[i]):
                            match = self.matches.pop(i)
                            print("**********MATCH**********")
                            print(match)
                            print("*************************")
                            break
                    if match is None:
                        continue

                    print(f"Ejecutando partida: {match.id} del Torneo : {self.name}, en puerto {match_server[1]}")
                    match_json = jsonable_encoder(match)
                    
                    response = requests.post(f"http://{match_server[0]}:{match_server[1]}/play_match", json=match_json).json()
                    print("VOY A ACOSTARME 5 SEC")
                    time.sleep(5)
                    print("ME DESPERTE")
                    self.UpdateCurrentData()
                    self.executed_matches[match_server[0]] = match
                    self.SetPlayerStatus(match, True)
                
                else:
                    #Asumo q la partida se demora por lo tanto paro el servidor y la repito 
                    self.matches.append(executed_match[match_server[0]])
                    self.UpdateCurrentData()
                    print(response)
        
        self.score = {player.id : 0 for player in self.players}
        for server in self.env.match_servers:
            response = requests.get(f"http://{server[0]}:{server[1]}/winners/{self.name}").json()
            self.process_score(response, end=True)
            print("*********SCORE********")
            print(self.score)
            print("**********************")
        
        self.setWinner()
        self.finished = True

        return "finished"
                

class Playoffs(Tournament):
    def __init__(self, env : Server_env, name = "", game : Game_Schema = None, type = "", players : list = [], tournament_data : Tournament_data = None):
        Tournament.__init__(self, env,name = name, game = game, type = type, players = players, tournament_data = tournament_data)
        self.CreateMatches()
        self.tournament_data.state.missing_matchs = self.matches
        self.player_status = { player.id : False for player in self.players }
        self.executed_matches = {}
    
    
    def CreateMatches(self):
        players = self.players[:]
        match_players = []
        aux = []
        count = 0
        for i in range(int(len(players)/self.game.amount_players)):
            for j in range(self.game.amount_players):
               player_k = random.choice(players)
               aux.append(player_k)
               players.remove(player_k)
            aux_1 = aux[:]
            match_players.append(tuple(aux_1))
            aux.clear() 
        for current_players in match_players:
            self.matches.append(Match_Schema(id=count, tournament_name=self.name, players=list(current_players), game=self.game))
            count += 1

    def process_score(self, winners, end = False):
        executed = False
        for match in winners.keys():
            if not end:
                for exec_match in self.executed_matches.values():
                    if exec_match.id == match:
                        executed = True
            if executed:
                continue
            for player in winners[match]:
                self.score[player] += 3

        self.tournament_data.statistics.score = self.score

    def setWinner(self):
        max = 0
        winner = None
        for player in self.score.keys():
            if self.score[player] > max:
                winner = player
                max = self.score[player]
        
        for player in self.players:
            if player.id == winner:
                self.tournament_data.statistics.winners = [player]
                self.tournament_data.statistics.bestPlayer = player
                self.tournament_data.state.finished = True
                self.UpdateCurrentData()
                break
    
    def Execute(self, firstTime = True):
        if firstTime:
            with open("./current_tour_data.json") as cdata_file:
                data_json = json.load(cdata_file)
            tour_data = jsonable_encoder(self.tournament_data)
            data_json["tournaments"].append(tour_data)
            self.sendData()
            with open("./current_tour_data.json", "w") as cdata_file:
                json.dump(data_json, cdata_file)
        
        client = docker.from_env()
        count = 0
        len_matches = len(self.matches)

        while len(self.matches) > 0:
            winners = []
            for match_server in self.env.match_servers:
                try:
                    response = requests.get(f"http://{match_server[0]}:{match_server[1]}/available").json()
                    print(response)
                except:
                    #el servidor de partidas fallo por alguna razon
                    self.env.add_match_server(match_server[1])
                    continue

                if response["available"]:
                    if match_server[0] in self.executed_matches.keys():
                        executed_match = self.executed_matches[match_server[0]]

                    match = None
                    played_matches = []
                    for i in range(len(self.matches)):
                        match = self.matches.pop(i)
                        print("**********MATCH**********")
                        played_matches.append(match)
                        print(match)
                        print("*************************")
                        break
                    if match is None:
                        continue

                    # print("************WINNERSSSS**************")
                    # print(winners)
        
                    print(f"Ejecutando partida: {match.id} del Torneo : {self.name}, en puerto {match_server[1]}")
                    match_json = jsonable_encoder(match)
                    
                    response = requests.post(f"http://{match_server[0]}:{match_server[1]}/play_match", json=match_json).json()
                    print("VOY A ACOSTARME 5 SEC")
                    time.sleep(5)
                    print("ME DESPERTE")
                    self.UpdateCurrentData()
                    self.executed_matches[match_server[0]] = match
                    winners.append(requests.get(f"http://{match_server[0]}:{match_server[1]}/winners/{self.name}/{match.id}").json())
                
                else:
                    #Asumo q la partida se demora por lo tanto paro el servidor y la repito 
                    self.matches.append(executed_match[match_server[0]])
                    self.UpdateCurrentData()
                    print(response)
        
        if len(self.matches) == 0:
            print("***************WINNERS***************")
            print(winners)
            # for match_server in self.env.match_servers:
            #     if match_server[0] in self.executed_matches.keys():
            #         for i in range(len_matches):
            #             winners = requests.get(f"http://{match_server[0]}:{match_server[1]}/winners/{self.name}/{i}").json()     
            winners_of_round = []
            print("****************************")
            print("Me quede sin partidas")
            # print("************WINNERSSSS**************")
            # print(winners)
            time.sleep(10)
            try:
                for lista in winners:
                    print("Estoy comprobando los que pasaron de ronda")
                    print("****************LISTA DE GANADORES***************")
                    for plyer in lista.values():
                        winners_of_round.append({"id": plyer[0], "type": "random"})
                        print(winners_of_round)
                self.players.clear()
                for players in winners_of_round:
                    self.players.append(players)
                
                if len(self.players) == 1:
                    return "finished"
                self.CreateMatches()
                print("************************************************")
                print("")
                print("Cree las nuevas partidas de la siguiente ronda")
                self.Execute(False)
            
            except Exception as e:
                print(e)
                self.score = {player.id : 0 for player in self.players}
                for server in self.env.match_servers:
                    response = requests.get(f"http://{server[0]}:{server[1]}/winners/{self.name}").json()
                    self.process_score(response, end=True)
                    print("*********SCORE********")
                    print(self.score)
                    print("**********************")
                
                self.setWinner()
                self.finished = True

                return "finished"
                
        # en verdad todo esto va en except de arriba, esta aqui solo para probar
        # self.score = {player.id : 0 for player in self.players}
        # for server in self.env.match_servers:
        #     response = requests.get(f"http://{server[0]}:{server[1]}/winners/{self.name}").json()
        #     self.process_score(response, end=True)
        #     print("*********SCORE********")
        #     print(self.score)
        #     print("**********************")
        
        # self.setWinner()
        # self.finished = True

        # return "finished"