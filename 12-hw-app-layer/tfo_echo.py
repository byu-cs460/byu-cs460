#!/usr/bin/env python3

import binascii
import getopt
import socket
import sys

# From /usr/include/linux/tcp.h 
TCP_FASTOPEN = 23 # Enable FastOpen on listeners
# From /usr/include/x86_64-linux-gnu/bits/socket.h 
MSG_FASTOPEN = 0x20000000 # Send data in TCP SYN.

def listen_echo(port):
    '''
    Listen, accept clients, and echo messages.
    '''

    s = socket.socket()
    s.setsockopt(socket.IPPROTO_TCP, TCP_FASTOPEN, 100)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port))
    s.listen()
    while True:
        c, (src, sport) = s.accept()
        while True:
            data = c.recv(4096)
            c.send(data)
        c.close()


def send_once_tcp(dst, dport, data):
    '''
    Send a message with TCP.  Return the response.
    '''

    s = socket.socket()
    s.connect((dst, dport))
    s.send(data)
    return s.recv(4096)


def send_once_tfo(dst, dport, data):
    '''
    Send a message with TCP Fast Open (TFO).  Return the response.
    '''

    s = socket.socket()
    s.sendto(data, MSG_FASTOPEN, (dst, dport))
    return s.recv(4096)


def usage():
    sys.stderr.write('''Usage:
%s [ -f ] <server> <port> <msg> [ <msg>... ]
%s -l <port>
''' % (sys.argv[0], sys.argv[0]))


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'fbl')
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    opts = dict(opts)

    # server
    if '-l' in opts:
        if len(args) < 1:
            usage()
            sys.exit(1)
        port = int(args[0])
        listen_echo(port)

    # server
    else:
        if len(args) < 2:
            usage()
            sys.exit(1)
        server = args[0]
        port = int(args[1])
        msgs = args[2:]

        if '-b' in opts:
            data = bytes()
            for msg in msgs:
                data += binascii.unhexlify(msg)
        else:
            data = ' '.join([msg for msg in msgs]).encode('utf-8')

        if '-f' in opts:
            response_data = send_once_tfo(server, port, data)
        else:
            response_data = send_once_tcp(server, port, data)

        if '-b' in opts:
            print(binascii.hexlify(response_data))
        else:
            print(response_data.decode('utf-8'))

if __name__ == '__main__':
    main()
