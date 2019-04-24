import os
from socket import *

def receive_file():
	downloaded = ""
	while True:
		buf = s.recv(4096).decode()
		if(buf == "<EOF>"):
			break
		downloaded += buf

	return downloaded

def byt(text):
	return bytes(text, "utf-8")

HOST = "177.183.170.34" # 177.183.170.34
PORT = 33001
s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT))

print("Checking for Updates...")

try: # File exists
	local_client = open("client.py", "r")
	local_data = local_client.read()
	local_client.close()
	downloaded_client = receive_file()

	if(not local_data == downloaded_client): # If is not updated
		print("Updating Client...")
		local_client = open("client.py", "w")
		local_client.write(downloaded_client)
		local_client.close()
		s.send(byt(downloaded_client))

	else: #is updated
		s.send(byt(local_data))

except: # File doesn't exists
	print("Downloading updated client")
	s.send(byt("<new>"))
	downloaded_client = receive_file()
	local_client = open("client.py", "w")
	local_client.write(downloaded_client)
	local_client.close()

serial = s.recv(4096).decode()
chm = []
for element in serial:
	chm.append(str(ord(element)))

file = open("auth", "w")
file.write(",".join(chm))
file.close()

os.system("python client.py")
