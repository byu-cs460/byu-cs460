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

class SimHost(Host):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_ip(self, pkt, intf):
        try:
            ip = IP(pkt)
            if ip.proto == IP_PROTOS.icmp:
                self.log(f'Received ICMP packet from {ip.src} on {intf}.')
        except:
            traceback.print_exc()
        super().handle_ip(pkt, intf)

    def send_icmp_echo(self, src, dst, id, seq, ttl=None):
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
        dsts_for_a = ('10.0.0.3', '10.20.0.25',
                '10.20.0.34', '10.20.1.20',
                '10.20.3.1', '10.20.0.2',
                '10.20.0.11', '10.20.0.150',
                '10.20.0.7', '10.20.0.75')

        loop = asyncio.get_event_loop()

        loop.call_later(3, self.log, 'START')
        loop.call_later(17, self.log, 'STOP')

        i = 4
        for dst in dsts_for_a:
            args = ('10.0.0.2', dst, 1, 1, None)
            loop.call_later(i, self.send_icmp_echo, *args)
            i += 1

        args1 = ('10.0.0.2', '10.40.0.2', 1, 1, None)
        args2 = ('10.0.0.2', '10.40.0.2', 1, 1, 1)

        loop.call_later(i, self.send_icmp_echo, *args1)
        loop.call_later(i+1, self.send_icmp_echo, *args2)
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--router', '-r',
            action='store_const', const=True, default=False,
            help='Act as a router by forwarding IP packets')
    args = parser.parse_args(sys.argv[1:])

    hostname = socket.gethostname()
    if hostname == 'a':
        cls = SimHostA
    else:
        cls = SimHost

    host = cls(args.router)
    host.schedule_items()
    host.run()

if __name__ == '__main__':
    main()
