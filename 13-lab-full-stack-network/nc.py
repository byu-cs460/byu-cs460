import sys

from mysocket import TCPSocket

class NetcatTCP:
    def __init__(self, local_addr, local_port,
            remote_addr, remote_port,
            send_ip_packet_func,
            output=sys.stdout,
            socket_cls=TCPSocket, **socket_args):

        self.output = output
        self.sock = socket_cls.connect(local_addr, local_port,
                remote_addr, remote_port,
                send_ip_packet_func, self.handle_data)

    def send(self, msg):
        msg = msg.encode('utf-8')
        self.sock.send(msg)

    def handle_data(self):
        msg = self.sock.recv(65536)
        msg = msg.decode('utf-8')
        self.output.write(msg)
        self.output.flush()
