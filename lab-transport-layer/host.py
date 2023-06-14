#!/usr/bin/python3

import os
import socket
import struct

from cougarnet.sim.host import BaseHost
from cougarnet.util import \
        mac_str_to_binary, mac_binary_to_str, \
        ip_str_to_binary, ip_binary_to_str

# From /usr/include/linux/if_ether.h:
ETH_P_IP = 0x0800 # Internet Protocol packet
ETH_P_ARP = 0x0806 # Address Resolution packet

# From /usr/include/net/if_arp.h:
ARPHRD_ETHER = 1 # Ethernet 10Mbps
ARPOP_REQUEST = 1 # ARP request
ARPOP_REPLY = 2 # ARP reply

# From /usr/include/linux/in.h:
IPPROTO_ICMP = 1 # Internet Control Message Protocol
IPPROTO_TCP = 6 # Transmission Control Protocol
IPPROTO_UDP = 17 # User Datagram Protocol

class Host(BaseHost):
    def __init__(self, ip_forward: bool):
        super().__init__()

        self._ip_forward = ip_forward

    def _handle_frame(self, frame: bytes, intf: str) -> None:
        pkt = frame[14:]
        self.handle_ip(pkt, intf)

    def handle_ip(self, pkt: bytes, intf: str) -> None:
        proto = pkt[9]
        dst = ip_binary_to_str(pkt[16:20])
        if not self.int_to_info[intf].ipv4_addrs or \
                dst != self.int_to_info[intf].ipv4_addrs[0]:
            return
        if proto == IPPROTO_TCP:
            self.handle_tcp(pkt)
        elif proto == IPPROTO_UDP:
            self.handle_udp(pkt)

    def handle_tcp(self, pkt: bytes) -> None:
        pass

    def handle_udp(self, pkt: bytes) -> None:
        pass

    def send_packet_on_int(self, pkt: bytes, intf: str, next_hop: str) -> None:
        src = mac_str_to_binary(self.int_to_info[intf].mac_addr)
        dst = b'\xff\xff\xff\xff\xff\xff'
        frame = dst + src + struct.pack('!H', ETH_P_IP) + pkt
        self.send_frame(frame, intf)

    def send_packet(self, pkt: bytes) -> None:
        intf = self.get_interface()
        self.send_packet_on_int(pkt, intf, None)
