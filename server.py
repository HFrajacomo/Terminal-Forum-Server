from socket  import *
from threading import Thread
import os
from os.path import expanduser
from subprocess import Popen
from threading import Thread

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
	return "Commands:\n\nshow\nchat\nsend <filedir>\nwrite <topic> <msg>\nread <topic> <page_num=0>\ndelete <topic>\nquit\nh(elp)\n"

# Prints all online users in chat
def whoson():
	global clients
	acc = "Online Users: \n\n"

	for sock in clients:
		if(clients[sock][0] == 1):
			acc += clients[sock][1] + "\n"

	return acc

# Server activities
def handle_client(client, IP):
	CHAT = 0
	FTP = False
	file_data = b''
	client.send(byt("Type a username"))
	username = client.recv(4096).decode()
	global clients
	clients[client] = [0, username]

	client.send(byt(help_message()))

	if(True):
	#try:
		while(True):

			if(not FTP):
				data = client.recv(4096).decode()
				command = data.split(" ")[0]

			else: # Handle FTP Stream
				data = client.recv(4096)
				if(data[-5:] == byt("<FTP>")):
					file_data += data[0:-5]
					file.write(file_data)
					file.close()
					client.send(byt("File successfully sent"))
					FTP = False
					continue
				else:
					file_data += data
					continue


			# Turn on chat mode
			if(command == "chat" and CHAT == 0):
				clients[client] = [1, username]
				client.send(byt("Connected to Chat!"))
				broadcast(username + " has connected\n", username)
				client.send(byt(whoson()))
				CHAT = 1
				continue


			# Chat send
			elif(CHAT == 1):
				if(data[0:2] == "/w"):
					client.send(byt(whoson()))
				if(data[0:2] == "/q"):
					client.send(byt("Disconnected from Chat!"))
					CHAT = 0
					clients[client] = [0, username]
					broadcast(username + " has disconnected\n", username)
				else:
					msg = username + ": " + data + "\n"
					broadcast(msg, username)
				continue
				
			# Temporary halt
			if(command == "show"):
				client.send(byt(show_topics()))
				continue

			# Activates FTP Stream
			elif(command == "send"):
				filename = "".join(" ".join(data.split(" ")[1:]).split("\\")[-1])
				filed = " ".join(data.split(" ")[1:])
				file = open(FILEDIR + filename, "wb")
				FTP = True
				client.send(byt("<FTP>" + filed))
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
HOST = '200.136.206.137'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
QUIT = False
Chat_Threads = []

if(not os.path.exists(POSTDIR)):
	os.system("mkdir Blogs")

if(not os.path.exists(FILEDIR)):
	os.system("mkdir Files")

s = socket(AF_INET, SOCK_STREAM) 
s.bind((HOST, PORT))  
s.listen(1)           
accept_connection()