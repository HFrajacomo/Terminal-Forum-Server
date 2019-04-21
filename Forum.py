import os
from socket import *

def byt(text):
	return bytes(text, "utf-8")

HOST = gethostbyname(getfqdn())
PORT = 33001
s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT))

print("Checking for Updates...")

try: # File exists
	local_client = open("client.py", "r")
	local_data = local_client.read()
	local_client.close()
	downloaded_client = s.recv(4096).decode()

	if(not local_data == downloaded_client): # If is updated
		print("Updating Client...")
		local_client = open("client.py", "w")
		local_client.write(downloaded_client)
		local_client.close()

except: # File doesn't exists
	print("Downloading updated client")
	downloaded_client = s.recv(4096).decode()
	local_client = open("client.py", "w")
	local_client.write(downloaded_client)
	local_client.close()

os.system("python client.py")
