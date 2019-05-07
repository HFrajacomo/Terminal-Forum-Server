import os
from socket import *

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

def receive_file():
	downloaded = ""
	while True:
		buf = s.recv(4096).decode()
		if(buf == "<CONERR>"):
			print("Couldn't connect to main server!")
			exit()			
		if(buf == "<EOF>"):
			break
		elif(buf[-5:] == "<EOF>"):
			downloaded += buf[0:-5]
			break
		downloaded += buf

	return downloaded

def byt(text):
	return bytes(text, "utf-8")


# Creates ip file
if(not os.path.isfile("ip.txt")):
	ipfile = open("ip.txt", "w")
	ipfile.write("IP=")
	ipfile.close()
	print("IP file created.\nOpen ip.txt and insert the server IP.\nLeave it blank to connect to localhost.\nRun this file again to connect.")
	exit()

HOST = read_ip_file() # 177.183.170.34
PORT = 33001
s = socket(AF_INET, SOCK_STREAM)
try:
	s.connect((HOST, PORT))
except ConnectionRefusedError:
	print("Couldn't find server!")
	exit()

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
		s.send(byt("<EOF>"))

	else: #is updated
		s.send(byt(local_data))
		s.send(byt("<EOF>"))

except: # File doesn't exists
	print("Downloading updated client")
	s.send(byt("<new>"))
	downloaded_client = receive_file()
	local_client = open("client.py", "w")
	local_client.write(downloaded_client)
	local_client.close()

serial = receive_file()
chm = []
for element in serial:
	chm.append(str(ord(element)))

file = open("auth", "w")
file.write(",".join(chm))
file.close()

os.system("python client.py")