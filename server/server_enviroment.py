import docker

class Server_env:
    def __init__(self):
        self.current_port = 0
        self.match_servers = []
        self.leader = ""
    
    def set_port(self, port):
        self.current_port = port
    def set_leader(self, url : str):
        self.leader = url
    
    def add_match_server(self, url : str):
        self.match_servers.append(url)
    
    def check_env(self):
        if len(self.match_servers) > 0:
            return True
        return False