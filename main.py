import docker

volumes = { '/var/run/docker.sock': { 'bind': '/var/run/docker.sock', 'mode': 'rw' } }
       
docker_client = docker.from_env()
cmd = ["python", "server_routes.py", str(5012)]
tour_server = docker_client.containers.run(
                        "tournament-server", 
                        detach= True, 
                        ports={f'{5012}/tcp': ("127.0.0.1", 5012)},
                        volumes=volumes,
                        command=cmd,
                    )