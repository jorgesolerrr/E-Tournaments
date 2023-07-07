import docker
import requests

print(requests.get(f"http://192.168.27.1:5024/available"))