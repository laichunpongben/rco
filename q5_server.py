from __future__ import print_function, division
import random
import socket


class Server(object):
	A, Z = 0, 25

	def __init__(self):
		nw = list(range(Server.A+1, Server.Z+2))
		self.NWS = [random.sample(nw, len(nw)) for _ in range(3)]

	def main(self, args):
		l, n, p = args.l, args.n, args.p

		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.bind((socket.gethostname(), l))
		serversocket.listen(5)
		print("listening: {0}".format(l))
		while 1:
			conn, addr = serversocket.accept()
			if conn is None:
				break

			buf = b''
			r = 0
			sum_ = 0
			while 1:
				buf = conn.recv(1024)
				if not buf:
					break
				c = self.req(buf)
				# print(buf[:-1].decode(), c)
				conn.send("{0}\r\n".format(c).encode())
				sum_ += c
				r += 1
				if r % p == 0:
					print("req: {0}, avg: {1:.2f}".format(r, sum_ / r))
				if r >= n:
					break
			conn.close()
		serversocket.close()

	def req(self, buf):
		c = 0
		l = Server.A
		r = Server.Z

		for i in range(len(self.NWS)):
			j = buf[i] - ord('A')
			l = max(j - 1, Server.A)
			r = min(j + 1, Server.Z)

			nw = self.NWS[i]
			c += nw[j]
			self.NWS[i] = self.swap(nw)
		return c

	@staticmethod
	def swap(nw):
		i, j = random.sample(range(Server.Z + 1), 2)
		nw[j], nw[i] = nw[i], nw[j]
		return nw

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-l', type=int, default=8001,
	                    help='port')
	parser.add_argument('-n', type=int, default=100000,
	                    help='')
	parser.add_argument('-p', type=int, default=10000,
	                    help='')

	args = parser.parse_args()

	server = Server()
	server.main(args)
