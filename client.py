from socket  import *
from threading import Thread
import os
import os.path

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

	try:
		while(not QUIT):
			sent = input()
			if(not CHAT and not FTP):
				os.system("cls" if os.name == 'nt' else 'clear')
			else:
				print()
			if(sent == "chat"):
				CHAT = True
			elif(sent == "/q"):
				CHAT = False
				os.system("cls" if os.name == 'nt' else 'clear')
			s.send(byt(sent))
	except(OSError, EOFError):
		return

def async_receive(conn):
	global QUIT
	global FTP

	while(not QUIT):
		received = conn.recv(4096).decode()

		if(received[0:5] == "<FTP>"):
			home = os.path.expanduser("~")
			filename = received[5:]
			file = open(home + "\\" + filename, "rb")
			file_data = file.read()
			conn.send(file_data)
			conn.send(byt("<FTP>"))
			continue


		if(received == "Quit"):
			QUIT = True
			global threads
			threads[0].join()
			print("Disconnected")
			conn.close()
			return

		print(received)

def join_all(thList):
	for th in thList:
		th.join()

QUIT = False
FTP = False
HOST = "200.136.206.137"
PORT = 33000
CHAT = False
threads = []
s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT))

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