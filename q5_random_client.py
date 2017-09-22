import socket
import random


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

    for i in range(100000):
        msg = random.choice(routes)
        clientsocket.send('{0}\n'.format(msg).encode())
        m = clientsocket.recv(1024)
    clientsocket.close()

if __name__ == '__main__':
    main()
