#!/usr/bin/env python3

import asyncio
import json
import socket

NEIGHBOR_CHECK_INTERVAL = 3
DV_TABLE_SEND_INTERVAL = 1
DV_PORT = 5016

from cougarnet.sim.host import BaseHost

from prefix import *
from mysocket import UDPSocket
from transporthost import TransportHost

class DVRouter(TransportHost):
    def __init__(self):
        super().__init__(True)

        self.my_dv = {}
        self.neighbor_dvs = {}

        self._dv_socks = {}

        # Forwarding table is initialized in Host.__init__();
        # Host is an ancestor class that handles IP Forwarding

        self._initialize_dv_sock()

        # Do any further initialization here

    def _initialize_dv_sock(self) -> None:
        '''Initialize the socket that will be used for sending and receiving DV
        communications to and from neighbors.
        '''

        for intf in self.physical_interfaces:
            sock = UDPSocket(
                    self.int_to_info[intf].ipv4_addrs[0],
                    DV_PORT,
                    self.send_packet, self._handle_msg)
            self._dv_socks[intf] = sock
            self.install_socket_udp(
                    self.int_to_info[intf].ipv4_addrs[0],
                    DV_PORT, sock)
            #XXX find a better way to accept packets
            self.install_socket_udp(
                    self.bcast_for_int(intf),
                    DV_PORT, sock)

    def init_dv(self):
        '''Set up our instance to work with the event loop, initialize our DV,
        and schedule our regular updates to be sent to neighbors.
        '''

        loop = asyncio.get_event_loop()

        # Schedule self.send_dv_next() to be called in 1 second and
        # self.update_dv_next() to be called in 0.5 seconds.
        loop.call_later(DV_TABLE_SEND_INTERVAL, self.send_dv_next)
        loop.call_later(DV_TABLE_SEND_INTERVAL - DV_TABLE_SEND_INTERVAL / 2,
                self.update_dv_next)

    def _handle_msg(self) -> None:
        ''' Receive and handle a message received on the UDP socket that is
        being used for DV messages.
        '''

        for intf in self._dv_socks:
            #XXX This check for non-zero buffer should go in recvfrom()
            if self._dv_socks[intf].buffer:
                data, addr, port = self._dv_socks[intf].recvfrom()
                self.handle_dv_message(data)

    def _send_msg(self, msg: bytes, dst: str) -> None:
        '''Send a DV message, msg, on our UDP socket to dst.'''

        #XXX We should probably use the correct socket in the future, but this
        # will work for now
        for intf in self._dv_socks:
            self._dv_socks[intf].sendto(msg, dst, DV_PORT)
            break

    def handle_dv_message(self, msg: bytes) -> None:
        pass

    def send_dv_next(self):
        '''Send DV to neighbors, and schedule this method to be called again in
        1 second (DV_TABLE_SEND_INTERVAL).
        '''

        self.send_dv()
        loop = asyncio.get_event_loop()
        loop.call_later(DV_TABLE_SEND_INTERVAL, self.send_dv_next)

    def update_dv_next(self):
        '''Update DV using neighbors' DVs.  Then schedule this method to be
        called again in 1 second (DV_TABLE_SEND_INTERVAL).
        '''

        self.update_dv()
        loop = asyncio.get_event_loop()
        loop.call_later(DV_TABLE_SEND_INTERVAL, self.update_dv_next)

    def handle_down_link(self, neighbor: str):
        self.log(f'Link down: {neighbor}')

    def resolve_neighbor_dvs(self):
        '''Return a copy of the mapping of neighbors to distance vectors, with
        IP addresses replaced by names in every neighbor DV.
        '''

        neighbor_dvs = {}
        for neighbor in self.neighbor_dvs:
            neighbor_dvs[neighbor] = self.resolve_dv(self.neighbor_dvs[neighbor])
        return neighbor_dvs

    def resolve_dv(self, dv: dict) -> dict:
        '''Return a copy of distance vector dv with IP addresses replaced by
        names.
        '''

        resolved_dv = {}
        for dst, distance in dv.items():
            if '/' not in dst:
                try:
                    dst = socket.getnameinfo((dst, 0), 0)[0]
                except:
                    pass
            resolved_dv[dst] = distance
        return resolved_dv

    def update_dv(self) -> None:
        pass

    def bcast_for_int(self, intf: str) -> str:
        ip_int = ip_str_to_int(self.int_to_info[intf].ipv4_addrs[0])
        ip_prefix_int = ip_prefix(ip_int, socket.AF_INET, self.int_to_info[intf].ipv4_prefix_len)
        ip_bcast_int = ip_prefix_last_address(ip_prefix_int, socket.AF_INET, self.int_to_info[intf].ipv4_prefix_len)
        bcast = ip_int_to_str(ip_bcast_int, socket.AF_INET)
        return bcast

    def send_dv(self) -> None:
        print('Sending DV')

def main():
    router = DVRouter()
    router.init_dv()
    router.run()

if __name__ == '__main__':
    main()
