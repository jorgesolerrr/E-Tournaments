import docker
import requests
from fastapi.encoders import jsonable_encoder
import time

class Middleware:
    def __init__(self, tourServer_amount = 3, matchServer_amount = 2, ports = ["5010", "5011", "5012"]):
        self.tourServer_amount = tourServer_amount
        self.matchServer_amount = matchServer_amount
        self.ports = ports
        self.servers = []
        self.tournaments = []
        self.match_portsInUse = []
        self.master = ""

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
        
        
        
        for server in self.servers:
            url = jsonable_encoder(server)
            time.sleep(1)
            ports = self._get_availables_ports(self.matchServer_amount)
            ports = {"ports" : ports}
            ports = jsonable_encoder(ports)
            r = requests.post(f"http://127.0.0.1:{server['port']}/SetEnv", params = {"servers" : self.matchServer_amount}, json = ports)
            response = requests.post(f"http://127.0.0.1:{server['port']}/SetTableConnection", json=url).json()
            
                
        
        url_toConnect = jsonable_encoder(self.servers[1])
        response = requests.post(f"http://127.0.0.1:{self.servers[0]['port']}/AddTourServer", json=url_toConnect)
        #conectar el ultimo con el primero para completar el ciclo
        url_toConnect = jsonable_encoder(self.servers[0])
        for i in range(2, len(self.servers)):
          response = requests.post(f"http://127.0.0.1:{self.servers[i]['port']}/AddTourServer", json=url_toConnect)


        self.master = self.servers[0]

    def CreateTournament(self, name : str, type : str, game, players : list):
        server_available = requests.get(f"http://127.0.0.1:{self.master['port']}/FindAvailableServer").json()
        if server_available:

            tournament = {
                  "name": name,
                  "type": type,
                  "game": game,
                  "players": players,
                }

            tournament = jsonable_encoder(tournament)
            available_port = server_available.split(':')[1]
            response = requests.post(f"http://127.0.0.1:{available_port}/create_tournament", json=tournament).json()
            self.tournaments.append((name, available_port))
        else:
            raise Exception("Not server available")
        
    def executeTournament(self, name):
        for tournament in self.tournaments:
            if tournament[0] == name:
                time.sleep(1)
                response = requests.get(f"http://127.0.0.1:{tournament[1]}/execute/{tournament[0]}")

def main():
    mdw = Middleware()
    mdw.set_tournament_env()
    players = [
    {
      "id": 0,
      "type": "random"
    },
    {
      "id": 1,
      "type": "random"
    },
    {
      "id": 2,
      "type": "random"
    },
    {
      "id": 3,
      "type": "random"
    },
    {
      "id": 4,
      "type": "random"
    }

  ]
    mdw.CreateTournament("LaLiga", "league", {"amount_players": 2, "name": "TicTacToe"}, players)
    mdw.executeTournament("LaLiga")
main()


{
  "name": "LaLiga",
  "type": "league",
  "game": {
    "amount_players": 2,
    "name": "TicTacToe"
  },
  "players": [
    {
      "id": 0,
      "type": "random"
    },
    {
      "id": 1,
      "type": "random"
    },
    {
      "id": 2,
      "type": "random"
    },
    {
      "id": 3,
      "type": "random"
    },
    {
      "id": 4,
      "type": "random"
    }

  ],
  "match_servers": 2,
  "ports": [
    5020,
    5021
  ]
}
# container = client.containers.run('nombre_de_la_imagen',
# volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}})