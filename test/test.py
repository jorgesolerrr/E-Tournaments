
import socket



class Listener():
    def __init__(self):
        self.tour_list = []
        self.matchs_list = []
        self.netMan_list = []
    
    # def BroadCast(self):
    #     # self.get_network_name()
    #     target_ip = "172.23.0.0/16"
    #     print("**********************************LA RED ES********************************")
    #     print(target_ip)
    #     # Crear una solicitud ARP para la red objetivo
    #     arp = ARP(pdst=target_ip)

    #     print("********************ARP********************")
    #     # Crear un paquete Ethernet
    #     ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    #     # Combinar paquete Ethernet y solicitud ARP
    #     packet = ether/arp
    #     # Enviar paquete y obtener respuesta
    #     result = srp(packet, timeout=3, verbose=0)[0]

    #     # Crear una lista de direcciones IP y MAC
    #     ip_addresses = []
    #     ports = []
    #     for sent, received in result:
    #         ip_addresses.append(received.psrc)
        
    #     print("*****************LOS IP DE LA RED******************")
    #     print(ip_addresses)
        
    #     for ip in ip_addresses:
    #         nm = nmap.PortScanner()
    #         nm.scan(hosts= ip, arguments='-p-')
    #         for port in nm[ip]['tcp']:
    #             if nm[ip]['tcp'][port]['state'] == 'open':
    #                 ports.append(port)
    #                 print("****************LOS PUERTOS***************")
    #                 print(port)
    #                 if 5020 <= int(port):
    #                     self.matchs_list.append(str(ip_addresses) + ":" + str(port))
    #                 if 5010 <= int(port) and int(port) < 5020:
    #                     self.tour_list.append(str(ip_addresses) + ":" + str(port))
        
    def Listen(self,socket):
        mensaje, direccion = socket.recvfrom(1024)
        print(f"Mensaje recibido: {mensaje.decode()} de {direccion}")

    # # def get_network_name(self):
    # #     hostname = socket.gethostname()
    # #     ip_adress = socket.gethostbyname(hostname)
    # #     return socket.getfqdn(ip_adress)
    

if __name__ == "__main__":
    a = Listener()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Configura el socket para escuchar en la dirección de broadcast de la red local en el puerto 12345
    sock.bind(('', 12345))
    while(True):
        a.Listen(sock)
