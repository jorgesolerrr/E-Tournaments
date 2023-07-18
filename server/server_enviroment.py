import docker
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class Server_env:
    def __init__(self):
        self.current_port = 0
        self.match_servers = []
        self.leader = ""
    
    def set_port(self, port):
        self.current_port = port

    def set_env(self, data):
        logger.info(str(data))
        for i in range(len(data["ip"])):
            self.match_servers.append((data["ip"][i], data["port"][i]))


            

    def set_leader(self, url : str):
        self.leader = url
    
    def add_match_server(self, url : str):
        ip, port = url.split(':')
        if (ip,port) in self.match_servers:
            logger.warning("ESTAS INTENTANDO AÑADIR UN SERVIDOR DE PARTIDA QUE YA ESTABA")
            return
        self.match_servers.append((ip, port))
        
    def check_env(self):
        if len(self.match_servers) > 0:
            return True
        return False