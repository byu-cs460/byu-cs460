#!/usr/bin/python3

import argparse
import asyncio
import os
import random
import socket
import sys
import traceback

from scapy.all import IP, Raw, TCP
from scapy.data import IP_PROTOS
from scapy.layers.inet import ETH_P_IP

from mysocket import TCPSocket, TCP_STATE_ESTABLISHED
from transporthost import TransportHost

START_TIME = 4

A_PORT = 4321
A_INITIAL_SEQ = 13850
B_PORT = 1234
B_INITIAL_SEQ = 492739
STEPS = 10
DOWNLOADS_DIR = 'downloads'

class FileSenderReceiver:
    def __init__(self, local_addr, local_port,
            remote_addr, remote_port,
            local_initial_seq, remote_initial_seq,
            fast_retransmit, window, filename,
            send_ip_packet_func, log):

        self.filename = filename
        size = os.stat(filename).st_size
        steps = [i * size//STEPS for i in range(STEPS)] + [size + 1]
        sent_steps = steps[:]
        recvd_steps = steps[:]

        class SimTCPSocket(TCPSocket):
            def __init__(self1, *args, **kwargs):
                super(SimTCPSocket, self1).__init__(*args, **kwargs)
                try:
                    self1.__sent_step_index = 0
                    self1.__recvd_step_index = 0
                    self1.__acked_step_index = 0
                    self1.__sent_steps = steps[:]
                    self1.__recvd_steps = steps[:]
                    self1.__acked_steps = steps[:]
                except:
                    traceback.print_exc()

            def handle_ack(self1, pkt):
                try:
                    ip = IP(pkt)
                    tcp = ip.getlayer(TCP)
                    tot = self1.relative_seq_self(tcp.ack)
                    if self1.__acked_step_index < len(self1.__acked_steps) and \
                            tot >= self1.__acked_steps[self1.__acked_step_index]:
                        if tot == size + 1:
                            self1.__acked_step_index = STEPS
                        pct = int(self1.__acked_step_index*100/STEPS)
                        log(f'{pct}% has been acked')
                        self1.__acked_step_index += 1
                except:
                    traceback.print_exc()
                super(SimTCPSocket, self1).handle_ack(pkt)

            def send_packet(self1, seq, ack, flags, data=b''):
                try:
                    tot = self1.relative_seq_self(seq) + len(data)
                    if self1.__sent_step_index < len(self1.__sent_steps) and \
                            tot >= self1.__sent_steps[self1.__sent_step_index]:
                        if tot == size + 1:
                            self1.__sent_step_index = STEPS
                        pct = int(self1.__sent_step_index*100/STEPS)
                        log(f'{pct}% has been sent')
                        self1.__sent_step_index += 1
                except:
                    traceback.print_exc()
                super(SimTCPSocket, self1).send_packet(seq, ack, flags, data=data)

            def handle_data(self1, pkt):
                try:
                    ip = IP(pkt)
                    tcp = ip.getlayer(TCP)
                    data = ip.getlayer(Raw)
                    tot = self1.relative_seq_other(tcp.seq) + len(data)
                    if self1.__recvd_step_index < len(self1.__recvd_steps) and \
                            tot >= self1.__recvd_steps[self1.__recvd_step_index]:
                        if tot == size + 1:
                            self1.__recvd_step_index = STEPS
                        pct = int(self1.__recvd_step_index*100/STEPS)
                        log(f'{pct}% has been recvd')
                        self1.__recvd_step_index += 1
                except:
                    traceback.print_exc()
                super(SimTCPSocket, self1).handle_data(pkt)

        self.sock = SimTCPSocket(local_addr, local_port,
                remote_addr, remote_port, TCP_STATE_ESTABLISHED,
                send_ip_packet_func, self.store_file_data,
                fast_retransmit=fast_retransmit, initial_cwnd=window)
        self.sock.bypass_handshake(local_initial_seq, remote_initial_seq)
        self.fh = None

    def prepare_to_receive(self):
        try:
            os.mkdir(DOWNLOADS_DIR)
        except FileExistsError:
            pass
        self.fh = open(os.path.join(DOWNLOADS_DIR, os.path.basename(self.filename)), 'wb')

    def store_file_data(self):
        if self.fh is not None:
            data = self.sock.recv(65535)
            self.fh.write(data)
            self.fh.flush()

    def send_file(self):
        with open(os.path.basename(self.filename), 'rb') as fh:
            while True:
                d = fh.read(3000)
                if not d:
                    break
                self.sock.send(d)


class SimHost(TransportHost):
    def schedule_items(self, window, fast_retransmit, filename):
        pass

class SimHostA(SimHost):
    def schedule_items(self, window, fast_retransmit, filename):
        app = FileSenderReceiver('10.0.0.1', A_PORT,
                '10.0.0.2', B_PORT,
                A_INITIAL_SEQ, B_INITIAL_SEQ,
                window, fast_retransmit, filename,
                self.send_packet, self.log)

        self.install_socket_tcp('10.0.0.1', A_PORT, '10.0.0.2', B_PORT, app.sock)
        loop = asyncio.get_event_loop()
        loop.call_later(START_TIME, self.log, 'START')
        loop.call_later(START_TIME + 2, app.send_file)

class SimHostB(SimHost):
    def schedule_items(self, window, fast_retransmit, filename):
        app = FileSenderReceiver('10.0.0.2', B_PORT,
                '10.0.0.1', A_PORT,
                B_INITIAL_SEQ, A_INITIAL_SEQ,
                window, fast_retransmit, filename,
                self.send_packet, self.log)

        self.install_socket_tcp('10.0.0.2', B_PORT, '10.0.0.1', A_PORT, app.sock)
        loop = asyncio.get_event_loop()
        loop.call_later(START_TIME + 1, app.prepare_to_receive)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--router', '-r',
            action='store_const', const=True, default=False,
            help='Act as a router by forwarding IP packets')
    parser.add_argument('--file', '-f',
            action='store', type=str,
            help='Act as a router by forwarding IP packets')
    parser.add_argument('--window', '-w',
            action='store', type=int,
            help='Initial congestion window size (bytes)')
    parser.add_argument('--fast-retransmit',
            action='store', type=str, choices=('on', 'off'),
            default='off',
            help='Congestion window size (bytes)')
    args = parser.parse_args(sys.argv[1:])

    hostname = socket.gethostname()
    if hostname == 'a':
        cls = SimHostA
    elif hostname == 'b':
        cls = SimHostB
    else:
        cls = SimHost

    if args.fast_retransmit == 'on':
        fast_retransmit = True
    else:
        fast_retransmit = False


    host = cls(args.router)
    host.schedule_items(fast_retransmit, args.window, args.file)
    host.run()

if __name__ == '__main__':
    main()
