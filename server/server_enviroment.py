import docker

class Server_env:
    def __init__(self):
        self.match_servers = []
        self.containers = []
    
    def set_env(self, data):
        for i in range(len(data["ip"])):
            self.match_servers.append((data["ip"][i],data["port"][i]))
        # docker_client = docker.from_env()
        # try:
        #    image = docker_client.images.get("match-server")
        # except:
        #     raise Exception("Match server is not available")
        # if len(ports) != servers_amount:
        #     raise Exception("Equal number of ports and servers needed")
        
        # try:
        #     for i in range(servers_amount):
        #         cmd = ["python", "match_server.py", str(ports[i])]
        #         match_server = docker_client.containers.run("match-server", ports={f'{ports[i]}/tcp': ('127.0.0.1', ports[i])}, detach= True, command=cmd)
        #         server_info = docker_client.api.inspect_container(match_server.id)
        #         container_ip = server_info['NetworkSettings']['IPAddress']
        #         self.containers.append(match_server)
        #         self.match_servers.append((container_ip, ports[i]))
        # except:
        #     raise Exception("Something went wrong running containers")

        return "success"
    
    def add_match_server(self, port):
        docker_client = docker.from_env()
        try:
           image = docker_client.images.get("match-server")
        except:
            raise Exception("Match server is not available")
        cmd = ["python", "match_server.py", str(port)]
        match_server = docker_client.containers.run("match-server", ports={f'{port}/tcp': ('127.0.0.1', port)}, detach= True, command=cmd)
        self.match_servers.append((match_server, port))
    
    def check_env(self):
        if len(self.match_servers) > 0:
            return True
        return False