from mysocket import TCPListenerSocket

class EchoServerTCP:
    def __init__(self, local_addr, local_port, install_client_sock,
            send_ip_packet_func, **socket_kwargs):

        #XXX hack to override native _notify_on_data() for socket multiplexing
        def do_nothing():
            pass

        self.sock = TCPListenerSocket(local_addr, local_port,
                self.handle_new_client, send_ip_packet_func,
                do_nothing, **socket_kwargs)

        self._install_client_sock = install_client_sock

    def handle_new_client(self, local_addr, local_port,
            remote_addr, remote_port, sock):

        self._install_client_sock(local_addr, local_port,
                remote_addr, remote_port, sock)

        #XXX hack to override native _notify_on_data() for socket multiplexing
        def _notify_on_data():
            self.handle_data(sock)
        sock._notify_on_data = _notify_on_data

    def handle_data(self, sock):
        data = sock.recv(65536)
        if data:
            sock.send(data)
