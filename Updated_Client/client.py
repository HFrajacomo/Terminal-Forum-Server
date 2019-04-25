from socket  import *
from threading import Thread, Event
import os
import os.path
import sys
from platform import system
import colorama
import sys
from getpass import getpass
import re
from datetime import datetime

# Filters tags in text
def filter_tag(text):
	return re.sub(r'<\w*>', "***", text)


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

def match(b_array, pat):
    i_aux = 0
    for i in range(0,len(b_array)):
        for j in range(0,len(pat)):
            if(not(chr(b_array[i + i_aux]) == chr(pat[j]))):
                i_aux = 0
                j=0
                break
            else:
                i_aux += 1
            if(j == len(pat)-1):
                return True

    return False


def byt(text):
	return bytes(text, "utf-8")

def async_send():
	global QUIT
	global CHAT
	global REQ_COLOR
	
	username = ""

	while(not QUIT):
		if(not CHAT):
			sent = input()
		else:
			sent = filter_tag(getpass("\r"))
			if(sent == "/cc"):
				EV.clear()
				s.send(byt(sent))
				REQ_COLOR = True
				EV.set()
				continue
			if(sent[0:2] == "/h"):
				s.send(byt(sent))
				continue
			t = datetime.now()
			print(chat_color + "|" + username + "|" + ": " + sent + "\t[" + str(t.hour) + ":" + str(t.minute) + "]\n")

		EV.wait()

		if(not CHAT and not FTP):
			os.system("cls" if os.name == 'nt' else 'clear')
		else:
			print()
		if(sent[0:2] == "/l"):
			try:
				username = sent.split(" ")[1]
			except:
				pass
		if(sent == "chat"):
			CHAT = True
		elif(sent == "/q"):
			CHAT = False
			os.system("cls" if os.name == 'nt' else 'clear')
		elif(CHAT and sent == "/c"):
			os.system("cls" if os.name == 'nt' else 'clear')
			continue
		s.send(byt(sent))


def async_receive(conn):
	global QUIT
	global FTP
	global threads
	global chat_color
	global REQ_COLOR
	file_data = b''
	filename = ""
	acc = ""

	while(not QUIT):
		if(not FTP):
			received = conn.recv(4096).decode()
		else:
			received = conn.recv(4096)
			if(received[-7:] == byt("<FTPin>")):
				file_data += received[0:-7]
				file = open(DOWNLOADDIR + filename, "wb")
				file.write(file_data)
				file.close()
				file_data = b''
				FTP = False
				print("File downloaded successfully")
				EV.set()
				continue
			else:
				file_data += received
				continue

		
		# Color protocol
		# Enter chat
		if(received[0:7] == "<Color>" and not REQ_COLOR):
			EV.wait()
			chat_color = received.split("<Color>")[1]
			received = received.split("<Color>")[2]
		elif(REQ_COLOR):
			chat_color = conn.recv(5).decode()
			received = conn.recv(4096).decode()
			REQ_COLOR = False
			continue
		

		# Out-going FTP
		if(received[0:5] == "<FTP>"):
			EV.clear()
			received = conn.recv(4096).decode()
			filename = received
			try:
				file = open(UPLOADDIR + filename, "rb")
				file_data = file.read()
				conn.send(file_data)
				conn.send(byt("<FTP>"))
				EV.set()
			except:
				conn.send(byt("<FTP>"))
				EV.set()
			continue

		# Prepare Incoming FTP
		if(received[-7:] == "<FTPin>" and not FTP):
			EV.clear()
			filename = received[0:-7]
			conn.send(byt("<FTPin>"))
			FTP = True
			continue

		if(received == "<AuthF>"):
			QUIT = True
			print("Authentication Failed!")
			threads[0].join()
			conn.close()
			return			

		if(received == "Quit"):
			QUIT = True
			print("Disconnected")
			threads[0].join()
			conn.close()
			return

		print(received)

def join_all(thList):
	for th in thList:
		th.join()

def read_config():
	file = open("config.cfg", "r")
	data = file.read().split("\n")
	file.close()
	dwd = ""
	upd = ""

	for line in data:
		aux = line.split("=")
		try:
			if(aux[0] == "Download_Directory"):
				dwd = aux[1]
			if(aux[0] == "Upload_Directory"):
				upd = aux[1]
		except:
			print("Fatal Error reading config file\n")
			exit()

	# No pre-config
	if(dwd == ""):
		dwd = os.getcwd()
	if(upd == ""):
		if(system() == "Windows"):
			upd = os.path.expanduser("~") + "\\Desktop\\"
		else:
			upd = os.path.expanduser("~") + "/Desktop/"

	# Slash fix
	if(system() == "Windows"):
		if(not dwd[-1] == "\\"):
			dwd += "\\"
		if(not upd[-1] == "\\"):
			upd += "\\"
	else:
		if(not dwd[-1] == "/"):
			dwd += "/"
		if(not upd[-1] == "/"):
			upd += "/"

	return dwd, upd


colorama.init(autoreset=True)

QUIT = False
FTP = False
HOST = read_ip_file()
PORT = 33000
CHAT = False
REQ_COLOR = False
chat_color = ""
EV = Event()
EV.set()

threads = []
s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT))

try:
	file = open("auth", "r")
	auth = file.read()
	file.close()
except:
	print("Invalid client. Download the official client!")
	exit()

aux = ""
for element in auth.split(","):
	aux += chr(int(element))

os.remove("auth")
s.send(byt(aux))

# Creates config file
if(not os.path.isfile("config.cfg")):
	cfgfile = open("config.cfg", "w")
	cfgfile.write("Download_Directory=\nUpload_Directory=")
	cfgfile.close()

DOWNLOADDIR, UPLOADDIR = read_config()

s.send(byt(system()))
received = s.recv(1024).decode() 
print(received)

try:
	threads.append(Thread(target=async_send))
	threads.append(Thread(target=async_receive, args=(s,)))

	for th in threads:
		th.start()

	for th in threads:
		th.join()

except KeyboardInterrupt:
	QUIT = True
	s.close()
	exit()