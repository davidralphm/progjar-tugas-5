from socket import *
import socket
import time
import sys
import logging
import threading
from http import HttpServer

class BackendList:
	def __init__(self):
		self.servers=[]

		self.servers.append(('127.0.0.1',9001))
		self.servers.append(('127.0.0.1',9002))
		self.servers.append(('127.0.0.1',9003))
		self.servers.append(('127.0.0.1',9004))
		self.servers.append(('127.0.0.1',9005))
		
		self.current=0

	def getserver(self):
		s = self.servers[self.current]
		
		# print(s)
		
		self.current=self.current+1
		
		if (self.current>=len(self.servers)):
			self.current=0
		
		return s

class ProcessTheClient(threading.Thread):
	def __init__(self, connection, address, backend_sock):
		self.connection = connection
		self.address = address
		self.backend_sock = backend_sock

		# self.backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# self.backend_sock.settimeout(30)			
		# self.backend_sock.connect(backend_address)

		threading.Thread.__init__(self)

	def run(self):
		# To upstream
		while True:
			try:
				datafrom_client = self.connection.recv(32)
				# print('From client')
				# print(datafrom_client)

				if datafrom_client:
					self.backend_sock.sendall(datafrom_client)
				# else:
				if len(datafrom_client) < 32:
					# print('From client done!')
					break

			except Exception as e:
				#print(str(e))
				pass

		# To client
		while True:
			try:
				datafrom_backend = self.backend_sock.recv(32)
				# print('From backend')
				# print(datafrom_backend)
				# print(len(datafrom_backend))

				if datafrom_backend:
					self.connection.sendall(datafrom_backend)
				# else:
				if len(datafrom_backend) < 32:
					# print('From backend done!')
					break

			except Exception as e:
				#print(str(e))
				pass

		self.backend_sock.close()
		self.connection.close()

		return

class Server(threading.Thread):
	def __init__(self):
		# self.the_clients = []
		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.backend = BackendList()

		threading.Thread.__init__(self)

	def run(self):
		self.my_socket.bind(('0.0.0.0', 55555))
		self.my_socket.listen(1)

		while True:
			connection, client_address = self.my_socket.accept()

			backend_address = self.backend.getserver()

			backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			backend_sock.settimeout(30)			
			backend_sock.connect(backend_address)

			# logging.warning(f"{client_address} connecting to {backend_address}")
			
			try:
				ProcessTheClient(connection, client_address, backend_sock).start()
				#logging.warning("connection from {}".format(client_address))
			except Exception as err:
				#logging.error(err)
				pass


def main():
	svr = Server()
	svr.start()

if __name__=="__main__":
	main()