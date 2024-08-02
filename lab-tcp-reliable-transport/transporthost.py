import struct

from cougarnet.util import \
        ip_str_to_binary, ip_binary_to_str

from headers import IPv4Header, UDPHeader, TCPHeader, \
        IP_HEADER_LEN, UDP_HEADER_LEN, TCP_HEADER_LEN, \
        TCPIP_HEADER_LEN, UDPIP_HEADER_LEN
from host import Host
from mysocket import UDPSocket, TCPSocketBase

class TransportHost(Host):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.socket_mapping_udp = {}
        self.socket_mapping_tcp = {}

    def handle_tcp(self, pkt: bytes) -> None:
        ip_hdr = pkt[:IP_HEADER_LEN]
        src_ip = ip_binary_to_str(ip_hdr[12:16])
        dst_ip = ip_binary_to_str(ip_hdr[16:20])

        tcp_hdr = pkt[IP_HEADER_LEN:TCPIP_HEADER_LEN]
        src_port, = struct.unpack('!H', tcp_hdr[:2])
        dst_port, = struct.unpack('!H', tcp_hdr[2:4])
        sock = self.socket_mapping_tcp[(dst_ip, dst_port, src_ip, src_port)]
        sock.handle_packet(pkt)

    def handle_udp(self, pkt: bytes) -> None:
        pass

    def install_socket_udp(self, local_addr: str, local_port: int,
            sock: UDPSocket) -> None:
        self.socket_mapping_udp[(local_addr, local_port)] = sock

    def install_listener_tcp(self, local_addr: str, local_port: int,
            sock: TCPSocketBase) -> None:
        self.socket_mapping_tcp[(local_addr, local_port, None, None)] = sock

    def install_socket_tcp(self, local_addr: str, local_port: int,
            remote_addr: str, remote_port: int, sock: TCPSocketBase) -> None:
        self.socket_mapping_tcp[(local_addr, local_port, \
                remote_addr, remote_port)] = sock

    def no_socket_udp(self, pkt: bytes) -> None:
        pass

    def no_socket_tcp(self, pkt: bytes) -> None:
        pass
