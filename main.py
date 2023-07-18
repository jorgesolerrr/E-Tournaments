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

# Ruta del archivo que contiene el módulo
ruta_modulo = getcwd() + "/Games/TicTacToe.py"

#Nombre del módulo
nombre_modulo = "TicTacToe"

# Crea una especificación de módulo
especificacion = importlib.util.spec_from_file_location(nombre_modulo, ruta_modulo)

# Crea un objeto de módulo a partir de la especificación
modulo = importlib.util.module_from_spec(especificacion)
aux = inspect.getmembers(modulo)
# Carga el módulo

especificacion.loader.exec_module(modulo)
# aux = inspect.getmembers(modulo, inspect.isclass)
aux1 = inspect.getmembers(IGame, inspect.isfunction)
inspect.ge
aux1 = [func_name for func_name, func in aux1]
print(aux1)
# Usa la clase del módulo