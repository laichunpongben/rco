#!/usr/bin/python3

from __future__ import print_function, division
import socket
import random
import math


# THRESHOLD = (81 - 3) * 2 / (1 + math.sqrt(5)) + 3
THRESHOLD = 50

def p_new(score):
    if score < THRESHOLD:
        return 1.0
    else:
        return 0.0


def main():
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((socket.gethostname(), 8001))

    routes = []
    for i in range(65, 91):
        for j in range(-1, 2):
            if 65 <= i + j <= 90:
                for k in range(-1, 2):
                    if 65 <= i + j + k <= 90:
                        c = chr(i) + chr(i+j) + chr(i+j+k)
                        routes.append(c)

    scores = {k: 0 for k in routes}

    route = 'AAA'
    for i in range(100000):
        p = p_new(scores[route])
        if random.uniform(0, 1) <= p:
            route = random.choice(routes)
        clientsocket.send('{0}\n'.format(route).encode())
        buf = clientsocket.recv(1024)
        if buf:
            score = int(buf[:-2])
            scores[route] = score
    clientsocket.close()

if __name__ == '__main__':
    main()
