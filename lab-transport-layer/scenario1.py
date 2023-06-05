#!/usr/bin/python3

import argparse
import asyncio
import binascii
import random
import socket
import sys
import traceback

from scapy.all import Ether, ICMP, IP, UDP, Raw, UDP
from scapy.data import IP_PROTOS
from scapy.layers.inet import ETH_P_IP

from echoserver import EchoServerUDP
from nc import NetcatUDP
from transporthost import TransportHost


A_PORT = random.randint(1024, 65535)
B_PORT = 1234
C_PORT = random.randint(1024, 65535)

class SimHost(TransportHost):
    def _handle_frame(self, frame, intf):
        try:
            eth = Ether(frame)
            if eth.type == ETH_P_IP:
                ip = eth.getlayer(IP)
                if ip.dst == self.int_to_info[intf].ipv4_addrs[0]:
                    if ip.proto == IP_PROTOS.udp:
                        udp = ip.getlayer(UDP)
                        payload = bytes(udp.getlayer(Raw))
                        msg1 = payload.decode('utf-8')
                        self.log(f'Host received UDP msg ({ip.src}:{udp.sport} -> {ip.dst}:{udp.dport}): {msg1}')
                    elif ip.proto == IP_PROTOS.icmp:
                        icmp = ip.getlayer(ICMP)
                        payload = bytes(icmp.payload)
                        payload_str = binascii.hexlify(payload).decode('utf-8')
                        try:
                            ip2 = IP(payload)
                            if ip2.proto == IP_PROTOS.udp:
                                udp2 = ip2.getlayer(UDP)
                                payload2 = bytes(udp2.getlayer(Raw))
                                msg2 = payload2.decode('utf-8')
                                payload_str = \
                                        f'UDP msg ({ip2.src}:{udp2.sport} -> {ip2.dst}:{udp2.dport}): {msg2}'
                        except:
                            pass
                        self.log(f'Host received ICMP (type={icmp.type}, code={icmp.code}), ' + \
                                payload_str)
        except:
            traceback.print_exc()
        super(SimHost, self)._handle_frame(frame, intf)

    def schedule_items(self):
        pass

class SimHostA(SimHost):
    def schedule_items(self):
        a_args = ('abcdefghijklmnop', '10.0.0.2', B_PORT)

        class SimNetcatUDP(NetcatUDP):
            def handle_data(_self):
                msg, remote_addr, remote_port = _self.sock.recvfrom()
                msg1 = msg.decode('utf-8')
                self.log(f'Netcat received UDP msg from {remote_addr}:{remote_port}: {msg1}')

            def sendto(_self, msg, addr, port):
                try:
                    self.log(f'Netcat sending UDP msg to {addr}:{port}: {msg}')
                except:
                    pass
                super(SimNetcatUDP, _self).sendto(msg, addr, port)

        client = SimNetcatUDP('10.0.0.1', A_PORT, self.send_packet)
        self.install_socket_udp('10.0.0.1', A_PORT, client.sock)

        loop = asyncio.get_event_loop()
        loop.call_later(4, self.log, 'START')
        loop.call_later(5, client.sendto, *a_args)
        loop.call_later(7, client.sendto, *a_args)
        loop.call_later(9, self.log, 'STOP')

class SimHostB(SimHost):
    def schedule_items(self):

        class SimEchoServerUDP(EchoServerUDP):
            def handle_data(_self):
                try:
                    msg, remote_addr, remote_port = _self.sock.recvfrom()
                    _self.sock.buffer.insert(0, (msg, remote_addr, remote_port))
                    msg1 = msg.decode('utf-8')
                    self.log(f'Echo server received UDP msg from {remote_addr}:{remote_port}: {msg1}')
                except:
                    traceback.print_exc()
                super(SimEchoServerUDP, _self).handle_data()

        def setup_server():
            server = SimEchoServerUDP('10.0.0.2', B_PORT, self.send_packet)
            self.install_socket_udp('10.0.0.2', B_PORT, server.sock)

        loop = asyncio.get_event_loop()
        loop.call_later(6, setup_server)

class SimHostC(SimHost):
    def schedule_items(self):
        a_args = ('abcdefghijklmnop', '10.0.0.2', B_PORT)

        class SimNetcatUDP(NetcatUDP):
            def handle_data(_self):
                msg, remote_addr, remote_port = _self.sock.recvfrom()
                msg1 = msg.decode('utf-8')
                self.log(f'Netcat received UDP msg from {remote_addr}:{remote_port}: {msg1}')

            def sendto(_self, msg, addr, port):
                try:
                    self.log(f'Netcat sending UDP msg to {addr}:{port}: {msg}')
                except:
                    pass
                super(SimNetcatUDP, _self).sendto(msg, addr, port)

        client = SimNetcatUDP('10.0.0.3', C_PORT, self.send_packet)
        self.install_socket_udp('10.0.0.3', C_PORT, client.sock)

        loop = asyncio.get_event_loop()
        loop.call_later(8, client.sendto, *a_args)

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
