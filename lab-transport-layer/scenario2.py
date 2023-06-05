#!/usr/bin/python3

import argparse
import asyncio
import random
import socket
import sys
import traceback

from scapy.all import Ether, ICMP, IP, Raw, TCP
from scapy.data import IP_PROTOS
from scapy.layers.inet import ETH_P_IP

from mysocket import TCPListenerSocket, TCPSocket, TCP_STATE_ESTABLISHED, TCP_FLAGS_ACK
from transporthost import TransportHost


B_PORT = 1234

class SimHost(TransportHost):
    def _handle_frame(self, frame, intf):
        try:
            eth = Ether(frame)
            if eth.type == ETH_P_IP:
                ip = eth.getlayer(IP)
                if ip.dst == self.int_to_info[intf].ipv4_addrs[0]:
                    if ip.proto == IP_PROTOS.tcp:
                        tcp = ip.getlayer(TCP)
                        flags = tcp.sprintf('%TCP.flags%')
                        self.log(f'Host received TCP packet ({ip.src}:{tcp.sport} -> {ip.dst}:{tcp.dport})' + \
                                f'    Flags: {flags}, Seq={tcp.seq}, Ack={tcp.ack}')
        except:
            traceback.print_exc()
        super(SimHost, self)._handle_frame(frame, intf)

    def connect_and_install(self, local_addr, local_port,
            remote_addr, remote_port,
            send_ip_packet_func, notify_on_data_func):

        sock = TCPSocket.connect(local_addr, local_port,
                remote_addr, remote_port,
                send_ip_packet_func, notify_on_data_func)
        self.install_socket_tcp(local_addr, local_port, remote_addr, remote_port, sock)

    def send_packet_as_if_connected(self, local_addr, local_port,
            remote_addr, remote_port,
            send_ip_packet_func, notify_on_data_func):

        sock = TCPSocket(local_addr, local_port,
                remote_addr, remote_port, TCP_STATE_ESTABLISHED,
                send_ip_packet_func, notify_on_data_func)
        self.install_socket_tcp(local_addr, local_port, remote_addr, remote_port, sock)
        sock.send_packet(random.randint(0, 0xffffffff),
                random.randint(0, 0xffffffff), TCP_FLAGS_ACK, b'')

    def do_nothing(self):
        pass


class SimHostA(SimHost):
    def schedule_items(self):
        args1 = ('10.0.0.1', random.randint(1024, 65536), '10.0.0.2', B_PORT,
                self.send_packet, self.do_nothing)
        args2 = ('10.0.0.1', random.randint(1024, 65536), '10.0.0.2', B_PORT,
                self.send_packet, self.do_nothing)
        args3 = ('10.0.0.1', random.randint(1024, 65536), '10.0.0.2', B_PORT,
                self.send_packet, self.do_nothing)

        loop = asyncio.get_event_loop()
        loop.call_later(4, self.log, 'START')
        loop.call_later(5, self.connect_and_install, *args1)
        loop.call_later(7, self.connect_and_install, *args2)
        loop.call_later(8, self.send_packet_as_if_connected, *args3)
        loop.call_later(10, self.log, 'STOP')

class SimHostB(SimHost):
    def schedule_items(self):

        def setup_server():
            sock = TCPListenerSocket('10.0.0.2', B_PORT,
                    self.install_socket_tcp,
                    self.send_packet, self.do_nothing)
            self.install_listener_tcp('10.0.0.2', B_PORT, sock)

        loop = asyncio.get_event_loop()
        loop.call_later(6, setup_server)

class SimHostC(SimHost):
    def schedule_items(self):
        args = ('10.0.0.3', random.randint(1024, 65535), '10.0.0.2', B_PORT,
                self.send_packet, self.do_nothing)

        loop = asyncio.get_event_loop()
        loop.call_later(9, self.connect_and_install, *args)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--router', '-r',
            action='store_const', const=True, default=False,
            help='Act as a router by forwarding IP packets')
    args = parser.parse_args(sys.argv[1:])

    hostname = socket.gethostname()
    if hostname == 'a':
        cls = SimHostA
    elif hostname == 'b':
        cls = SimHostB
    elif hostname == 'c':
        cls = SimHostC
    else:
        cls = SimHost

    host = cls(args.router)
    host.schedule_items()
    host.run()

if __name__ == '__main__':
    main()
