from socket  import *
from threading import Thread
import os
from os.path import expanduser
from subprocess import Popen
from threading import Thread
from datetime import datetime

# Fast bytes convertion
def byt(text):
	return bytes(text, "utf-8")

# Waits for new connections
def accept_connection():
	global IPS
	global connections
	global QUIT
	global clients

	try:
		while(not QUIT):
			client, client_address = s.accept()
			print(str(client_address) + " has connected.")
			client.send(byt("Connected\n"))
			clients[client] = [0, ""]
			IPS.append(client_address)
			connections[client_address] = Thread(target=handle_client, args=(client,client_address))
			connections[client_address].start()
	except KeyboardInterrupt:
		for con in connections.values():
			con.join()
		exit()


# Add Post
def a_post(username, topic, msg):
	global POSTDIR

	try:
		if(os.path.isfile(POSTDIR + topic + ".txt")):
			file = open(POSTDIR + topic + ".txt", "a")
			file.write(username + ": " + msg + "\n")
			file.close()
		else:
			file = open(POSTDIR + topic + ".txt", "w")
			file.write(username + ": " + msg + "\n")
			file.close()
		return True

	except:
		print("Exception in Adding Post")
		return False

# Remove Post
# Deletes last message sent to a topic
def rm_post(username, topic):
	global POSTDIR

	if(os.path.isfile(POSTDIR + topic + ".txt")):
		file = open(POSTDIR + topic + ".txt", "r")
		data = file.readlines()
		size = len(data)
		data.reverse()
		file.close()

		for i in range(0, size):
			if(data[i].split(":")[0] == username):
				data.pop(i)
				break

		data.reverse()
		file = open(POSTDIR + topic + ".txt", "w")

		for line in data:
			file.write(line)
		file.close()

		return True
	else:
		return False

# Read Post
def rd_post(topic, page=0):
	global POSTDIR
	page_data = []
	page_count = 0

	if(os.path.isfile(POSTDIR + topic + ".txt")):
		file = open(POSTDIR + topic + ".txt", "r")
		data = file.readlines()
		if(data == [] or data == None):
			return "Topic is empty"

		size = len(data)
		data.reverse()
		file.close()

		for i in range(0, size):
			if(page_count == 10):
				page -= 1
				page_count = 0
			else:
				page_count += 1

			if(page == 0):
				page_data.insert(0, data[i])

			if(page == 0 and page_count == 10):
				return "\n".join(page_data)
		return "\n".join(page_data)
	else:
		return "Topic doesn't exist"

# View topic names
def show_topics():
	global POSTDIR

	folders = ""

	for r,d,f in os.walk(POSTDIR):
		for blog in f:
			blog = "".join(blog.split(".")[0])
			folders += blog + "\n"

	if(folders != ""):
		return folders
	else:
		return "Forum is empty"

# Sends a message to all users in chat mode
def broadcast(msg, username):
	global clients

	for sock in clients:
		if(clients[sock][1] == username):
			continue
		if(clients[sock][0] == 1):
			sock.send(byt(msg))

# Returns help message
def help_message():
	return "Commands:\n\nshow\nchat\nupload <filedir>\nfiles\ndownload <file>\nwrite <topic> <msg>\nread <topic> <page_num=0>\ndelete <topic>\nquit\nh(elp)\n"

# Prints all online users in chat
def whoson():
	global clients
	acc = "Online Users: \n\n"

	for sock in clients:
		if(clients[sock][0] == 1):
			acc += clients[sock][1] + "\n"

	return acc

# Print chat help message
def print_chat_help():
	return "Type /q to quit\n/w to see who's online\n/c to clear chat windows\n"

# Check if file exists in _ref file
def check_file(name):
	ref = open(REFFILE, "r")

	for line in ref:
		if(line.split("\t")[0] == name):
			return True
	return False

# Removes an entry from _ref file
def update_file(name):
	ref = open(REFFILE, "r")
	acc = ""

	for line in ref:
		if(not line.split("\t")[0] == name):
			acc += line

	ref.close()
	ref = open(REFFILE, "w")
	ref.write(acc)
	ref.close()

# Server activities
def handle_client(client, IP):
	message_count = 0  # After 20 messages, show help message
	CHAT = 0
	FTP = False
	FTP_out = False
	file_data = b''
	client.send(byt("Type a username"))
	username = client.recv(4096).decode()
	global clients
	clients[client] = [0, username]

	client.send(byt(help_message()))

	if(True):
	#try:
		while(True):

			# To client FTP connection
			if(FTP_out):
				client.send(file.read())
				file.close()
				client.send(byt("<FTPin>"))
				FTP_out = False
				continue

			if(not FTP):
				data = client.recv(4096).decode()
				command = data.split(" ")[0]

			else: # Handle FTP Stream
				data = client.recv(4096)
				if(data[-5:] == byt("<FTP>")):
					file = open(FILEDIR + filename, "ab")
					file.write(data[0:-5])
					file.close()

					if(check_file(filename)):
						update_file(filename)

					ref = open(REFFILE, "a")
					if(os.path.getsize(FILEDIR + filename) < 1048576):
						ref.write(filename + "\t" + username + "\t" + str(round(os.path.getsize(FILEDIR + filename)/1024, 1)) + " kB" + "\t" + str(datetime.now())[0:-7] + "\n")
					else:
						ref.write(filename + "\t" + username + "\t" + str(round(os.path.getsize(FILEDIR + filename)/1048576, 1)) + " MB" + "\t" + str(datetime.now())[0:-7] + "\n")
					ref.close()
					client.send(byt("File successfully sent"))
					FTP = False
					file_data = b''
					continue
				else:
					file = open(FILEDIR + filename, "ab")
					file.write(data)
					file.close()
					continue


			# Turn on chat mode
			if(command == "chat" and CHAT == 0):
				clients[client] = [1, username]
				client.send(byt("Connected to Chat!"))
				broadcast(username + " has connected\n", username)
				client.send(byt(whoson()))
				CHAT = 1
				continue


			# Chat Mode
			elif(CHAT == 1):
				if(data[0:2] == "/w"):
					client.send(byt(whoson()))
					continue
				if(data[0:2] == "/q"):
					client.send(byt("Disconnected from Chat!"))
					CHAT = 0
					message_count = 0
					clients[client] = [0, username]
					broadcast(username + " has disconnected\n", username)
				else:
					message_count += 1
					msg = username + ": " + data + "\n"
					broadcast(msg, username)

					if(message_count >= 20):
						client.send(byt(print_chat_help()))
						message_count = 0
				continue
				
			if(command == "show"):
				client.send(byt(show_topics()))
				continue

			# Activates FTP Stream
			elif(command == "upload"):
				filename = "".join(" ".join(data.split(" ")[1:]).split("\\")[-1])
				filed = " ".join(data.split(" ")[1:])
				if(check_file(filename)):
					file = open(FILEDIR + filename, "wb")
					file.close()
				FTP = True
				client.send(byt("<FTP>" + filed))
				continue

			elif(command == "download"):
				filename = " ".join(data.split(" ")[1:])
				if(check_file(filename)):
					file = open(FILEDIR + filename, "rb")
					client.send(byt(filename + "<FTPin>"))
					FTP_out = True
					continue
				else:
					client.send(byt("File " + filename + " not found"))
					continue

			elif(command == "files"):
				ref = open(REFFILE, "r")
				client.send(byt(ref.read()))
				ref.close()
				continue

			elif(command == "write"):
				topic = data.split(" ")[1]
				msg = " ".join(data.split(" ")[2:])
				if(a_post(username, topic, msg)):
					client.send(byt("Message successfully sent\n"))
				else:
					client.send(byt("There was a problem in your message\n"))
				continue

			elif(command == "read"):
				topic = data.split(" ")[1]
				try:
					page_num = int(data.split(" ")[2])
				except IndexError:
					page_num = 0
				client.send(byt(rd_post(topic, page_num)))
				continue

			elif(command == "delete"):
				topic = data.split(" ")[1]
				if(rm_post(username, topic)):
					client.send(byt("Last message deleted\n"))
				else:
					client.send(byt("No user messages found\n"))

				continue
			elif(command == "quit"):
				client.send(byt("Quit"))
				print(str(IP) + " disconnected\n")
				return
			elif(command == "crash"):
				client.send(byt("Quit"))
				global QUIT
				QUIT = True
				return
			elif(command == "h" or command == "help"):
				client.send(byt(help_message()))
				continue


	'''			
	except:
		client.send(byt("Quit"))
		return
	'''


IPS = []
connections = {}
clients = {}
POSTDIR = os.getcwd() + "\\Blogs\\"
FILEDIR = os.getcwd() + "\\Files\\"
REFFILE = FILEDIR + "_ref"
HOST = gethostbyname(getfqdn()) # "177.183.170.34"
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
QUIT = False
Chat_Threads = []

if(not os.path.exists(POSTDIR)):
	os.system("mkdir Blogs")

if(not os.path.exists(FILEDIR)):
	os.system("mkdir Files")
if(not os.path.isfile(REFFILE)):
	reffile = open(FILEDIR + "_ref", "w")
	reffile.close()

s = socket(AF_INET, SOCK_STREAM) 
s.bind((HOST, PORT))  
s.listen(1)           
accept_connection()