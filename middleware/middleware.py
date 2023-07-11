import docker
import requests
from fastapi.encoders import jsonable_encoder
import time
import warnings

class Middleware:
    def __init__(self, tourServer_amount = 3, matchServer_amount = 3, ports = ["5010", "5011", "5012"]):
        self.tourServer_amount = tourServer_amount
        self.matchServer_amount = matchServer_amount
        self.ports = ports
        self.servers = []
        self.tournaments = []
        self.match_portsInUse = []
        self.master = ""
        self.match_servers = []
        self.set_tournament_env()

    def _get_availables_ports(self, amount : int):
        if len(self.match_portsInUse) == 0:
            result = [5020 + i for i in range(amount)]
            self.match_portsInUse += result
            return result
        else:
            aux_port = self.match_portsInUse[len(self.match_portsInUse) - 1] + 1 
            result = [aux_port + i for i in range(amount)]
            self.match_portsInUse += result
            return result
            

    def set_tournament_env(self):
        docker_client = docker.from_env()
        try: 
            tour_image = docker_client.images.get("tournament-server")
            match_image = docker_client.images.get("match-server")
        except:
            raise Exception("Match server or tournament server images not available")


        volumes = { '/var/run/docker.sock': { 'bind': '/var/run/docker.sock', 'mode': 'rw' } }
        for port in self.ports:
            cmd = ["python", "server_routes.py", str(port)]
            tour_server = docker_client.containers.run(
                                        "tournament-server", 
                                        detach= True, 
                                        ports={f'{port}/tcp': ("127.0.0.1", port)},
                                        volumes=volumes,
                                        command=cmd,
                                    )
            server_info = docker_client.api.inspect_container(tour_server.id)
            server_ip = server_info['NetworkSettings']['IPAddress']
            self.servers.append({"ip" : server_ip, "port" : port})
        
        ports = self._get_availables_ports(self.matchServer_amount)
        if len(self.match_servers) == 0:
            for i in range(self.matchServer_amount):
                cmd = ["python", "match_server.py", str(ports[i])]
                match_server = docker_client.containers.run("match-server", ports={f'{ports[i]}/tcp': ('127.0.0.1', ports[i])}, detach= True, command=cmd)
                server_info = docker_client.api.inspect_container(match_server.id)
                container_ip = server_info['NetworkSettings']['IPAddress']
                self.match_servers.append((container_ip, ports[i]))
        ips = [item[0] for item in self.match_servers]
        tports = [item[1] for item in self.match_servers]
        for server in self.servers:
            url = jsonable_encoder(server)
            time.sleep(1)
            # ports = self._get_availables_ports(self.matchServer_amount)
            # ports = {"ports" : ports}
            # ports = jsonable_encoder(ports)
            r = requests.post(f"http://127.0.0.1:{server['port']}/SetEnv", json = {"ip": ips, "port": tports})
            response = requests.post(f"http://127.0.0.1:{server['port']}/SetTableConnection", json=url).json()
            
                
        
        url_toConnect = jsonable_encoder(self.servers[1])
        response = requests.post(f"http://127.0.0.1:{self.servers[0]['port']}/AddTourServer", json=url_toConnect)
        #conectar el ultimo con el primero para completar el ciclo
        url_toConnect = jsonable_encoder(self.servers[0])
        for i in range(2, len(self.servers)):
          response = requests.post(f"http://127.0.0.1:{self.servers[i]['port']}/AddTourServer", json=url_toConnect)


        self.master = self.servers[0]

    def CreateTournament(self, name : str, type : str, game, players : list):
        count = len(self.tournaments)
        
        server_available = False
        while not server_available:
            if count - len(self.tournaments) == len(self.servers):
                warnings.warn("NO HAY SERVIDORES DE TORNEO DISPONIBLES, VOY A REINICIAR TODO")
                self.set_tournament_env()
                count = len(self.tournaments)

            current_port = self.servers[count % len(self.servers)]['port']
            server_available = requests.get(f"http://127.0.0.1:{current_port}/Active").json()    
            count += 1
            
        
        
        current_port = self.servers[(count - 1) % len(self.servers)]['port']
        tournament = {
                "name": name,
                "type": type,
                "game": game,
                "players": players,
            }

        tournament = jsonable_encoder(tournament)
        response = requests.post(f"http://127.0.0.1:{current_port}/create_tournament", json=tournament).json()
        self.tournaments.append((name, current_port))
        
            
        
    def executeTournament(self, name):
        for tournament in self.tournaments:
            if tournament[0] == name:
                time.sleep(1)
                response = requests.get(f"http://127.0.0.1:{tournament[1]}/execute/{tournament[0]}", params={"firstTime" : True})
        return tournament[1]

def main():
     mdw = Middleware()
    
#     players = [
#     {
#       "id": 0,
#       "type": "random"
#     },
#     {
#       "id": 1,
#       "type": "random"
#     },
#     {
#       "id": 2,
#       "type": "random"
#     },
#     {
#       "id": 3,
#       "type": "random"
#     },
#     {
#       "id": 4,
#       "type": "random"
#     }

#   ]
#     mdw.CreateTournament("LaChampions", "playoffs", {"amount_players": 2, "name": "TicTacToe"}, players)
#     mdw.executeTournament("LaChampions")
#main()


# {
#   "name": "LaChampions",
#   "type": "playoffs",
#   "game": {
#     "amount_players": 2,
#     "name": "TicTacToe"
#   },
#   "players": [
#     {
#       "id": 0,
#       "type": "random"
#     },
#     {
#       "id": 1,
#       "type": "random"
#     },
#     {
#       "id": 2,
#       "type": "random"
#     },
#     {
#       "id": 3,
#       "type": "random"
#     },
#     {
#       "id": 4,
#       "type": "random"
#     }

#   ],
#   "match_servers": 2,
#   "ports": [
#     5020,
#     5021
#   ]
# }
# container = client.containers.run('nombre_de_la_imagen',
# volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}})