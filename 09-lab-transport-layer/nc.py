from mysocket import UDPSocket

class NetcatUDP:
    def __init__(self, addr, port, send_ip_packet_func):
        self.sock = UDPSocket(addr, port,
                send_ip_packet_func, self.handle_data)

    def sendto(self, msg, addr, port):
        msg = msg.encode('utf-8')
        self.sock.sendto(msg, addr, port)

    def handle_data(self):
        msg, remote_addr, remote_port = self.sock.recvfrom()
        msg = msg.decode('utf-8')
        print(msg)
