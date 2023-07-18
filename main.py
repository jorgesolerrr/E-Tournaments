# import docker

# volumes = { '/var/run/docker.sock': { 'bind': '/var/run/docker.sock', 'mode': 'rw' } }
       
# docker_client = docker.from_env()
# cmd = ["python", "server_routes.py", str(5012)]
# tour_server = docker_client.containers.run(
#                         "tournament-server", 
#                         detach= True, 
#                         ports={f'{5012}/tcp': ("127.0.0.1", 5012)},
#                         volumes=volumes,
#                         command=cmd,
#                     )
from os import getcwd
import inspect
from abc import ABC, abstractmethod
import importlib.util

class IGame(ABC):
    def __init__(self):
        self.finished = False
        self.winners = None
        self.current = None

    @abstractmethod
    def SetState(self, players, current):
        pass

    @abstractmethod
    def GetMoves(self):
        pass

    @abstractmethod
    def SetMove(self, move):
        pass

    @abstractmethod
    def GameEnd(self):
        pass

    @abstractmethod
    def GetWinners(self):
        pass
from os import getcwd
def test():
    with open(getcwd() + "/Games/TicTacToe.py", "r") as f:
        content = f.read()
        
    exec(content)
    locals_var = locals()
    instance = type(locals_var["TicTacToe"])
    print(instance.__call__(locals_var["TicTacToe"]))


test()
# Ruta del archivo que contiene el módulo

# Usa la clase del módulo