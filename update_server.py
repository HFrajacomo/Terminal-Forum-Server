import os
from socket import *
from threading import Thread

def byt(text):
	return bytes(text, "utf-8")

def accept_connection():
	global connections
	try:
		while(not QUIT):
			client, client_address = s.accept()
			print(str(client_address) + " retrieved information.")
			connections[client_address] = Thread(target=handle_client, args=(client,client_address))
			connections[client_address].start()
	except KeyboardInterrupt:
		exit()


def handle_client(client, IP):
	global connections
	updated_client = open("Updated_Client/client.py", "r")
	client.send(byt(updated_client.read()))
	updated_client.close()
	connections.pop(IP)
	return

HOST = gethostbyname(getfqdn()) # "177.183.170.34"
PORT = 33001
ADDR = (HOST, PORT)
QUIT = False
connections = {}

s = socket(AF_INET, SOCK_STREAM) 
s.bind((HOST, PORT))  
s.listen(1)           
accept_connection()