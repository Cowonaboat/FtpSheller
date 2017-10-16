#!/usr/bin/env python

# nc.py - simulate the netcat command in python
# 
# Copyright (c) 2013 Darren Wurf
# 
# This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.
# 
# Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:
# 
#     1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
# 
#     2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
# 
#     3. This notice may not be removed or altered from any source distribution.

import socket
import errno
import argparse # replaces optparse in 2.7 onwards
import sys
import time
from threading import Thread

try:
    from Queue import Queue, Empty  # python 2.x
except ImportError:
    from queue import Queue, Empty  # python 3.x

# CLI options parsing
parser = argparse.ArgumentParser(
    description='nc.py: An implementation of NetCat in python'
)
parser.add_argument('-l', dest='listen', action='store_const', const=True,
                default=False, help='listen instead of connect')
parser.add_argument('hostname', help='IP or hostname to connect to')
parser.add_argument('port', help='port to connect to')
args = parser.parse_args()

class ReadAsync(object):
    def __init__(self, blocking_function, *args):
        self.args = args
        self.read = blocking_function

        self.thread = Thread(target=self.enqueue)
        self.queue = Queue()
        self.thread.daemon = True

        self.thread.start()

    def enqueue(self):
        # TODO: the queue can grow without limit, it should have an upper limit
        while True:
            buf = self.read(*self.args)
            self.queue.put(buf)

    def dequeue(self):
        # Throws an exeption called Empty if there's no data to be read
        return self.queue.get_nowait()

# Networking isn't correct, I'm sure this fails in some cases.
# See http://gogonetlive.com/pdf/gogoNET_LIVE/Martin_Levy.pdf
addr = socket.getaddrinfo(
    args.hostname,
    int(args.port),
    socket.AF_UNSPEC,   # IPv4/IPv6
    socket.SOCK_STREAM, # Only TCP
    0                   # No flags
)

family = addr[0][0]     # int representing family eg ipv4/ipv6
socktype = addr[0][1]   # int representing socket type eg tcp/udp
proto = addr[0][2]      # int representing protocol eg ssh (22)
sockaddr = addr[0][4]

if args.listen:
    # Accept connection
    s = socket.socket(family, socktype)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(sockaddr)
    s.listen(1)
    conn, addr = s.accept()
else:
    conn = socket.socket(family, socktype)
    conn.connect(sockaddr)

conn.setblocking(0)
stdin = ReadAsync(sys.stdin.readline)

while True:
    try:
        sys.stdout.write(conn.recv(4096))
    except socket.error,e:
        # POSIX: this error is raised to indicate no data available
        if e.errno != errno.EWOULDBLOCK:
            raise
    try:
        conn.send(stdin.dequeue())
    except Empty:
        time.sleep(0.1)

conn.close()
