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
import logging


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class Tournament(ABC):
    def __init__(self, env : Server_env, name = "", game : Game_Schema = None, type = "", players : list = [], tournament_data : Tournament_data = None):
        if tournament_data is None:
            self.name = name
            self.game = game
            self.type = type
            self.players = players
            self.score = {player.id : 0 for player in players}
            self.matches = []
            self.executed_matches = {}
            self.missing_matches = []
            self.tournament_data = Tournament_data( 
                                                name=name, type=type, 
                                                game= game, players=players,
                                                statistics=Stats_Schema(winners=[], score=self.score,
                                                                       bestPlayer=Player_Schema(id=-1, type=""), victories=[]),
                                                state=Tournament_State(finished=False, missing_matchs=self.missing_matches)    
                                            ) 
            self.finished = self.tournament_data.state.finished
        else:
            self.name = tournament_data.name
            self.game = tournament_data.game
            self.type = tournament_data.type
            self.players = tournament_data.players
            self.score = tournament_data.statistics.score
            self.matches = tournament_data.state.missing_matchs.copy()
            self.missing_matches = tournament_data.state.missing_matchs
            self.finished = tournament_data.state.finished
            self.tournament_data = tournament_data
            self.executed_matches = {}


        self.env = env
        with open("./games" + f"/{self.game.name}.py", "r") as f:
            content = f.read()
            f.close()
        self.game_code = content
        self.players_code = {}
        for player in self.players:
            if player.type in self.players_code.keys():
                continue
            with open("./players" + f"/{player.type}.py", "r") as f:
                content = f.read()
                f.close()
            self.players_code[player.type] = content

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
    def playerStat(self,match,status):
        pass
    @abstractmethod
    def setWinner(self):
        pass

    def sendData(self):
        with open("./table_connection.json") as table_file:
            data_json = json.load(table_file)
            table_file.close()
        response = requests.post(f"http://{data_json['next1']}/UpdateData")
        with open("./table_connection.json", "w") as table_file:
            json.dump(data_json, table_file)
            table_file.close()

    def AddTournamentToData(self):
        logger.info("ESTOY AÑADIENDO UN TORNEO A LA DATA")
        with open("./current_tour_data.json") as cdata_file:
            data_json = json.load(cdata_file)
            cdata_file.close()
        
        tour_data = jsonable_encoder(self.tournament_data)
        data_json["tournaments"].append(tour_data)

        with open("./current_tour_data.json", "w") as cdata_file:
            json.dump(data_json, cdata_file)
            cdata_file.close() 
        
        self.sendData()

    def UpdateCurrentData(self):
        logger.info("ESTOY ACTUALIZANDO MI DATA")
        with open("./current_tour_data.json") as cdata_file:
            data_json = json.load(cdata_file)
            cdata_file.close()
        for i in range(len(data_json["tournaments"])):
            if data_json["tournaments"][i]["name"] == self.name:
                data_json["tournaments"].pop(i)
                tour_data = jsonable_encoder(self.tournament_data)
                data_json["tournaments"].append(tour_data)
                print("**************DATA*********************")
                print(dict(self.tournament_data))
                print("***************************************")
                break
        
        with open("./current_tour_data.json", "w") as cdata_file:
            json.dump(data_json, cdata_file)
            cdata_file.close()
        self.sendData()

    def update_missing_matches(self, finished_matches):
        print("***************TRATANDO DE ACTUALIZAR JUGADORES DEL MATCH")
        exec_matches_schema = [match for match in self.missing_matches if match.id in finished_matches]
        print(exec_matches_schema)
        for match in exec_matches_schema:
            self.missing_matches.remove(match)

            try:
                #print(match)

                for player in match.players:
                    print("*****************ESTOY ACTUALIZANDO EL ESTADO DEL JUGADOR : " + str(player.id))
                    self.player_status[player.id] = False
            except AttributeError:
                print("*****************NO ACTUALICE ESTADO")
                pass

        
            

    def checkWinners(self):
        print("**********ESTOY CHEQUEANDO LOS WINNERS")
        count = 0
        for match_server in self.env.match_servers:
            try:
                current_exec_matches_schema = self.executed_matches[match_server]
            except KeyError:
                continue
            try:
                active = requests.get(f"http://{match_server[0]}:{match_server[1]}/active")
            except:
                unfinished_matches = [match[0] for match in current_exec_matches_schema if not match[1]]
                if len(unfinished_matches) > 0:
                    self.matches.extend(unfinished_matches)
                try:
                    for match in unfinished_matches:
                        self.SetPlayerStatus(match, False)
                except:
                    pass
                try:
                    self.env.match_servers.remove(match_server)
                except ValueError:
                    pass
                logger.error("ERROR TRATANDO DE CONECTARME CON :" + str(match_server))
                continue
            
            finished_matches = requests.get(f"http://{match_server[0]}:{match_server[1]}/executed_matches/{self.name}").json()
            print(f"--------> PARTIDAS EJECUTADAS EN EL SERVIDOR {match_server}")
            print(finished_matches)
            print("*********************************************************")
            if len(finished_matches) == 0:
                continue
            current_exec_matches = [match[0].id for match in self.executed_matches[match_server] if not match[1]]
            current_matches =  [matchID for matchID in current_exec_matches if str(matchID) in finished_matches.keys()]
            
            for match in self.executed_matches[match_server]:
                if match[0].id in current_matches:
                    match[1] = True
            count += len(current_matches)
            print("******************PARTIDAS NUEVAS QUE TERMINARON")
            print(current_matches)
            print("*****************************************************")
            
            winn = [winners for key, winners in finished_matches.items() if int(key) in current_matches]
            try:
                self.winners.update([winni[0] for winni in winn])
            except AttributeError:
                pass

            print("*************WINNERS PARA PROCESAR SU SCORE**********")
            print(winn)
            print("***********************************")
            self.process_score(winn)
            self.update_missing_matches(current_matches)

        if count == 0:
            return False
        if len(self.missing_matches) > 0:
            return True
        return False
class League(Tournament):
    def __init__(self, env : Server_env, name = "", game : Game_Schema = None, type = "", players : list = [], tournament_data : Tournament_data = None):
        Tournament.__init__(self, env,name= name, game=game, type=type, players=players, tournament_data=tournament_data)
        if tournament_data is None:
            self.CreateMatches()
            self.missing_matches = self.matches[:]
        self.tournament_data.state.missing_matchs = self.missing_matches
        self.player_status = { player.id : False for player in self.players }
        self.winners = []

    # def process_score(self, winners, end = False):
    #     executed = False
    #     for match in winners.keys():
    #         if not end:
    #             for exec_match in self.executed_matches.values():
    #                 if exec_match.id == match:
    #                     executed = True
    #         if executed:
    #             continue
    #         for player in winners[match]:
    #             self.score[player] += 3

    #     self.tournament_data.statistics.score = self.score
    def process_score(self, winners, end = False):
        print("**************PROCESANDO SCORE")
        executed = False
        for matchwinner in winners:
            if len(matchwinner)>1:
                for win in matchwinner:
                    try:
                        self.score[win] += 1
                    except KeyError:
                        self.score[str(win)] += 1
            else:
                try:
                    self.score[matchwinner[0]] += 3
                except KeyError:
                    self.score[str(matchwinner[0])] += 3

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
            players_code = set([self.players_code[player.type] for player in list(current_players)])
            self.matches.append(Match_Schema(id=count, tournament_name=self.name, players=list(current_players), game=self.game, game_code=self.game_code, players_code=players_code))
            count+=1

    def SetPlayerStatus(self, match, status):
        for player in match.players:
            self.player_status[player.id] = status
    
    def playerStat(self, match, status):
        self.SetPlayerStatus(match,status)
    def _checkAvailablePlayers(self, match):
        for player in match.players:
            if self.player_status[player.id]:
                return False
        return True

    def Execute(self, firstTime):
        try:
            if not firstTime:
                self.player_status = { player.id : False for player in self.players }
            
            while (len(self.matches) > 0) or (self.checkWinners()):
                if len(self.matches) > 0:
                    for match_server in self.env.match_servers:
                        # try:
                        try:
                            response = requests.get(f"http://{match_server[0]}:{match_server[1]}/active").json()
                        except Exception as e:
                            logger.error("ERRORRRR-----------------------> " + str(e))
                            try:
                                unfinished_matches = [match[0] for match in self.executed_matches[match_server] if not match[1]]
                            except KeyError:
                                unfinished_matches = []
                                
                            if len(unfinished_matches) > 0:
                                self.matches.extend(unfinished_matches)
                            
                            for match in unfinished_matches:
                                self.SetPlayerStatus(match, False)

                            try:
                                self.env.match_servers.remove(match_server)
                            except ValueError:
                                pass
                            logger.info("Los servidores de partida que quedan son : " + str(self.env.match_servers))
                            continue
                        if match_server not in self.executed_matches.keys():
                            self.executed_matches[match_server] = []
                        #     print(response)
                        # except:
                        #     #el servidor de partidas fallo por alguna razon
                        #     self.env.add_match_server(match_server[1])
                        #     continue
                        
                        # if response["available"]:
                        match = None
                        for i in range(len(self.matches)):
                            if self._checkAvailablePlayers(self.matches[i]):
                                match = self.matches.pop(i)
                                print("**********MATCH**********")
                                print(match)
                                print("*************************")
                                break
                        
                        if match is None:
                            print(self.player_status)
                            continue

                        print(f"Ejecutando partida: {match.id} del Torneo : {self.name}, en puerto {match_server[1]}")
                        match_json = jsonable_encoder(match)
                        
                        response = requests.post(f"http://{match_server[0]}:{match_server[1]}/play_match", json=match_json).json()
                        
                        print("************ME VOY A ACOSTAR A DORMIR 5 SEC")
                        time.sleep(5)
                        print("************ME DESPERTÉ")

                        # self.UpdateCurrentData()
                        self.executed_matches[match_server].append([match, False])
                        # self.winners.append(requests.get(f"http://{match_server[0]}:{match_server[1]}/winners/{self.name}/{match.id}").json())
                        # self.process_score(self.winners,False)
                        # self.winners.clear()
                        self.SetPlayerStatus(match, True)
                        print("**************VOY A CHEQUEAR SI HAY PARTIDAS TERMINADAS")
                        end = self.checkWinners()
                        self.UpdateCurrentData()
                    
                    if len(self.env.match_servers) == 0:
                        logger.error("No match servers available")
                        raise Exception("No match servers available")

                    
            
            # self.score = {player.id : 0 for player in self.players}
            # self.process_score(self.winners, end=True)
            # self.UpdateCurrentData()
            # print("*********SCORE********")
            # print(self.score)
            # print("**********************")
            
            self.setWinner()
            self.finished = True

            return "finished"
        except Exception as e:
            logger.error("ERROR EJECUTANDO EL TORNEO : " + str(e))
            return "ERROR"
                

class Playoffs(Tournament):
    def __init__(self, env : Server_env, name = "", game : Game_Schema = None, type = "", players : list = [], tournament_data : Tournament_data = None):
        Tournament.__init__(self, env,name = name, game = game, type = type, players = players, tournament_data = tournament_data)
        self.count = 0
        self.totalplayers = players
        self.tournament_data.state.missing_matchs = self.matches
        self.player_status = { player.id : False for player in self.players }
        self.executed_matches = {}
        self.winners = set()
        if tournament_data is None:
            self.score = {player.id : 0 for player in self.players}
            self.CreateMatches()
            self.missing_matches = self.matches[:]
    
    def playerStat(self, match, status):
        return super().playerStat(match, status)
    def CreateMatches(self):
        players = self.players[:]
        match_players = []
        aux = []
        for i in range(int(len(players)/self.game.amount_players)):
            for j in range(self.game.amount_players):
               player_k = random.choice(players)
               aux.append(player_k)
               players.remove(player_k)
            aux_1 = aux[:]
            match_players.append(tuple(aux_1))
            aux.clear() 
        for current_players in match_players:
            players_code = set([self.players_code[player.type] for player in list(current_players)])
            self.matches.append(Match_Schema(id=self.count, tournament_name=self.name, players=list(current_players), game=self.game, game_code=self.game_code, players_code=players_code))
        self.count += 1

    def process_score(self, winners, end = False):
        executed = False
        for matchwinner in winners:
                try:
                    self.score[matchwinner[0]] += 3
                except KeyError:
                    self.score[str(matchwinner[0])] += 3
                    
        self.tournament_data.statistics.score = self.score

    def getWinnersRound(self):
        print("******************CALCULANDO GANADORES DE LA RONDA")
        current_winners = [player for player in self.players if player.id in self.winners]
        print(current_winners)
        if len(current_winners) != len(self.players) // 2:
            try:
                aux = [player for player in self.players if player.id not in self.winners and self.score[player.id] == self.score[current_winners[0].id]]
            except KeyError:
                 aux = [player for player in self.players if player.id not in self.winners and self.score[str(player.id)] == self.score[str(current_winners[0].id)]]
            print("******************EL QUE FALTABA ERA")
            print(aux)
            print("*************************************")
            current_winners += aux
        
        return current_winners
    def setWinner(self):
        max = 0
        winner = None
        for player in self.score.keys():
            if self.score[player] > max:
                winner = player
                max = self.score[player]
        
        for player in self.totalplayers:
            if player.id == winner:
                self.tournament_data.statistics.winners = [player]
                self.tournament_data.statistics.bestPlayer = player
                self.tournament_data.state.finished = True
                self.UpdateCurrentData()
                break
    
    def Execute(self, firstTime = True):
        # if firstTime:
        #     with open("./current_tour_data.json") as cdata_file:
        #         data_json = json.load(cdata_file)
        #     tour_data = jsonable_encoder(self.tournament_data)
        #     data_json["tournaments"].append(tour_data)
        #     self.sendData()
        #     with open("./current_tour_data.json", "w") as cdata_file:
        #         json.dump(data_json, cdata_file)

        len_matches = len(self.matches)

        winners = []
        while (len(self.matches) > 0 or self.checkWinners()):
            if len(self.matches) > 0:
                for match_server in self.env.match_servers:
                    try:
                        response = requests.get(f"http://{match_server[0]}:{match_server[1]}/active").json()
                        if match_server not in self.executed_matches.keys():
                            self.executed_matches[match_server] = []
                    except Exception as e:
                        print("ERRORRRR-----------------------> " + str(e))
                        unfinished_matches = [match[0] for match in self.executed_matches[match_server] if not match[1]]
                        self.matches.extend(unfinished_matches)
                        continue
                    
                    

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
                    self.executed_matches[match_server].append([match, False])
                    print("**************VOY A CHEQUEAR SI HAY PARTIDAS TERMINADAS")
                    end = self.checkWinners()
                    self.UpdateCurrentData()

                if len(self.env.match_servers) == 0:
                    logger.error("No match servers available")
                    raise Exception("No match servers available")
        
        
        if len(self.matches) == 0:
            print("***************WINNERS***************")
            print(self.winners)
            # for match_server in self.env.match_servers:
            #     if match_server[0] in self.executed_matches.keys():
            #         for i in range(len_matches):
            #             winners = requests.get(f"http://{match_server[0]}:{match_server[1]}/winners/{self.name}/{i}").json()     
            print("****************************")
            print("Me quede sin partidas")
            # print("************WINNERSSSS**************")
            # print(winners)
            try:

                print("Estoy comprobando los que pasaron de ronda")
                print("****************LISTA DE GANADORES***************")
                
                winners_of_round = self.getWinnersRound()
                
                print("*******************WINNERS OF ROUNDS")
                print(winners_of_round)

                self.players.clear()
                self.winners.clear()
                for players in winners_of_round:
                    self.players.append(players)
                
                print("***************JUGADORES QUE PASAN DE RONDA")
                print(self.players)

                if len(self.players) == 1:
                   
                        
                    # self.process_score(self.winners, end=True)
                    self.setWinner()
                    self.finished = True
                    return "finished"
                self.CreateMatches()
                print("************************************************")
                print("")
                print("Cree las nuevas partidas de la siguiente ronda")
                self.Execute(False)
            
            except Exception as e:
                print(e)
                
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