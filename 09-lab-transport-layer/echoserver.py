from mysocket import UDPSocket

class EchoServerUDP:
    def __init__(self, addr, port, send_ip_packet_func):
        self.sock = UDPSocket(addr, port,
                send_ip_packet_func, self.handle_data)

    def handle_data(self):
        msg, remote_addr, remote_port = self.sock.recvfrom()
        self.sock.sendto(msg, remote_addr, remote_port)
