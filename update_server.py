import os
from socket import *
from threading import Thread
import random as rd
from time import sleep

# Returns ip in ipfile
def read_ip_file():
	try:
		ipfile = open("ip.txt", "r")
		ip_data = ipfile.read().replace("\n", "").split("=")[1]
		ipfile.close()
		if(ip_data == ""):
			return "127.0.0.1"
		return ip_data
	except:
		return "127.0.0.1"

def receive_file(client):
	downloaded = ""
	while True:
		buf = client.recv(4096).decode()
		if(buf == "<EOF>"):
			break
		elif(buf[-5:] == "<EOF>"):
			downloaded += buf[0:-5]
			break
		downloaded += buf

	return downloaded

def byt(text):
	return bytes(text, "utf-8")

def generate_serial(text):
	serial = ""
	text = text.replace("\t", "")
	text = text.replace("\n", "")
	text = text.replace(" ", "")
	text = text.replace("\r", "")
	for i in range(0, int(len(text)/4)):
		serial += chr(ord(text[i*4]) + int(rd.randint(0,2)))
	return serial

def get_valid_serial():
	file = open(CLIENTFILE, "r")
	data = file.read()
	data = data.replace("\t", "")
	data = data.replace("\n", "")
	data = data.replace(" ", "")
	data = data.replace("\r", "")
	file.close()

	return generate_serial(data)


def accept_connection():
	global connections
	global APP_CONNECTED

	listener = Thread(target=app_server_listener, args=(read_ip_file(),))
	listener.start()

	try:
		while(not QUIT):
			if(APP_CONNECTED):
				client, client_address = s.accept()
				print(str(client_address) + " retrieved information.")
				connections[client_address] = Thread(target=handle_client, args=(client,client_address))
				connections[client_address].start()
	except KeyboardInterrupt:
		exit()

def app_server_listener(HOST, AUTH_PORT=33002):
	global APP_CONNECTED
	global auths

	print("Listening to connections")

	while(not QUIT):
		if(is_socket_connected(auths)):
			sleep(10)
			continue
		if(not APP_CONNECTED):
			try:
				auths = socket(AF_INET, SOCK_STREAM)
				auths.connect((HOST, AUTH_PORT))
				APP_CONNECTED = True
				os.system("cls" if os.name == 'nt' else 'clear')
				print("App server connected")
			except:
				print("Waiting for connection")
				sleep(4)

def is_socket_connected(s):
	global APP_CONNECTED

	try:
		s.send(byt(""))
		return True
	except:
		print("App server disconnected")
		APP_CONNECTED = False
		return False


def handle_client(client, IP):
	global connections
	updated_client = open(CLIENTFILE, "r")
	data = updated_client.read()
	client.send(byt(data))
	updated_client.close()
	client.send(byt("<EOF>"))
	received = receive_file(client)

	if(received == "<new>"):
		serial = get_valid_serial()
	else:
		serial = generate_serial(received)
	
	connections.pop(IP)
	try:
		auths.send(byt(serial))
	except OSError:
		client.send(byt("<CONERR>"))
		return
	sleep(1)
	client.send(byt(serial))
	client.send(byt("<EOF>"))
	return

# User connection
APP_CONNECTED = False
HOST = read_ip_file() # "177.183.170.34"
PORT = 33001
AUTH_PORT = 33002
QUIT = False
connections = {}
CLIENTFILE = os.getcwd() + "\\Updated_Client\\client.py"

s = socket(AF_INET, SOCK_STREAM) 
s.bind((HOST, PORT))  
s.listen(1)     

auths = socket(AF_INET, SOCK_STREAM)

accept_connection()