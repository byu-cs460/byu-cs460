#!/usr/bin/python3

import argparse
import asyncio
import os
import socket
import sys
import traceback

from scapy.all import IP, ICMP
from scapy.data import IP_PROTOS 

from host import Host

START_TIME = 6

class SimHost(Host):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_ip(self, pkt, intf):
        try:
            ip = IP(pkt)
            if ip.proto == IP_PROTOS.icmp:
                icmp = ip.getlayer(ICMP)
                if icmp.type in (0, 8):
                    self.log(f'Received ICMP packet from {ip.src} on {intf}.')
        except:
            traceback.print_exc()
        super().handle_ip(pkt, intf)

    def send_icmp_echo(self, src, dst, id, seq, ttl=None):
        self.log(f'Sending ICMP packet to {dst}')
        ip = IP(src=src, dst=dst, proto=IP_PROTOS.icmp)
        if ttl is not None:
            ip.ttl = ttl
        icmp = ICMP(type=8, id=id, seq=seq)
        pkt = ip / icmp / b'0123456789'

        self.send_packet(bytes(pkt))

    def schedule_items(self):
        pass

class SimHostA(SimHost):
    def schedule_items(self):
        args = ('10.0.0.2', '10.0.2.2', 1, 1)

        loop = asyncio.get_event_loop()
        loop.call_later(START_TIME, self.log, 'START')
        loop.call_later(START_TIME + 1, self.send_icmp_echo, *args)
        
class SimHostD(SimHost):
    def schedule_items(self):
        args = ('10.0.2.2', '10.0.0.2', 1, 1)

        loop = asyncio.get_event_loop()
        loop.call_later(START_TIME + 2, self.send_icmp_echo, *args)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--router', '-r',
            action='store_const', const=True, default=False,
            help='Act as a router by forwarding IP packets')
    args = parser.parse_args(sys.argv[1:])

    hostname = socket.gethostname()
    if hostname == 'a':
        cls = SimHostA
    elif hostname == 'd':
        cls = SimHostD
    else:
        cls = SimHost

    host = cls(args.router)
    host.schedule_items()
    host.run()

if __name__ == '__main__':
    main()
