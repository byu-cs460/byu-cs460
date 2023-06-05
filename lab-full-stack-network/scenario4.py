#!/usr/bin/python3

import argparse
import asyncio
import random
import socket
import sys
import traceback

from scapy.all import ARP, Ether, IP, Raw, TCP
from scapy.data import IP_PROTOS
from scapy.layers.inet import ETH_P_IP

from echoserver import EchoServerTCP
from host import Host, ETH_P_ARP, ARPOP_REQUEST, ARPOP_REPLY
from nc import NetcatTCP
from transporthost import TransportHost

START_TIME = 6

B_PORT = 4567

class SimHost(TransportHost):
    def _handle_frame(self, frame, intf):
        try:
            eth = Ether(frame)
            if eth.type == ETH_P_IP:
                ip = eth.getlayer(IP)
                if ip.dst == self.int_to_info[intf].ipv4_addrs[0]:
                    if ip.proto == IP_PROTOS.tcp:
                        tcp = ip.getlayer(TCP)
                        data = ip.getlayer(Raw)
                        if data is not None:
                            data = bytes(data).decode('utf-8')
                            data = data[:20]
                            if len(data) > 20:
                                data += f'... Len={len(data)})'
                        else:
                            data = ''
                        flags = tcp.sprintf('%TCP.flags%')
                        self.log(f'Received TCP packet ({ip.src}:{tcp.sport} -> {ip.dst}:{tcp.dport})' + \
                                f'    Flags: {flags}, Seq={tcp.seq}, Ack={tcp.ack}, Data={data}')
            #elif eth.type == ETH_P_ARP:
            #    arp = eth.getlayer(ARP)
            #    if arp.op == ARPOP_REQUEST:
            #        op = 'REQUEST'
            #        self.log(f'Received ARP {op} from {arp.psrc}/{arp.hwsrc} for {arp.pdst} on {intf}.')
        except:
            traceback.print_exc()
        super(SimHost, self)._handle_frame(frame, intf)

    def start_nc(self, remote_addr, remote_port):
        intf = self.get_interface()
        local_addr = self.int_to_info[intf].ipv4_addrs[0]
        local_port = random.randint(1024, 65536)

        nc = NetcatTCP(local_addr, local_port,
                remote_addr, remote_port,
                self.send_packet)
        self.install_socket_tcp(local_addr, local_port, remote_addr, remote_port, nc.sock)
        self.nc = nc

    def start_echo(self, local_port):
        intf = self.get_interface()
        local_addr = self.int_to_info[intf].ipv4_addrs[0]

        echo = EchoServerTCP(local_addr, local_port,
                self.install_socket_tcp,
                self.send_packet)
        self.install_listener_tcp(local_addr, local_port, echo.sock)
        self.echo = echo

    def send_to_nc(self, msg):
        self.nc.send(msg)

    def schedule_items(self):
        pass

class SimHostA(SimHost):

    def schedule_items(self):
        args = ('10.0.2.2', B_PORT)

        loop = asyncio.get_event_loop()
        loop.call_later(START_TIME, self.log, 'START')
        loop.call_later(START_TIME + 2, self.start_nc, *args)
        loop.call_later(START_TIME + 3, self.send_to_nc, 'hello world (A)')
        loop.call_later(START_TIME + 6, self.send_to_nc, 'hello Provo (A)')

class SimHostB(SimHost):

    def schedule_items(self):
        args = ('10.0.2.2', B_PORT)

        loop = asyncio.get_event_loop()
        loop.call_later(START_TIME + 4, self.start_nc, *args)
        loop.call_later(START_TIME + 5, self.send_to_nc, 'hello internet (B)')
        loop.call_later(START_TIME + 7, self.send_to_nc, 'hello BYU (B)')

class SimHostD(SimHost):
    def schedule_items(self):
        args = (B_PORT,)

        loop = asyncio.get_event_loop()
        loop.call_later(START_TIME + 1, self.start_echo, *args)

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
    elif hostname == 'd':
        cls = SimHostD
    else:
        cls = SimHost

    host = cls(args.router)
    host.schedule_items()
    host.run()

if __name__ == '__main__':
    main()
