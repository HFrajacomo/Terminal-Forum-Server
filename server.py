from socket  import *
from threading import Thread
import os
from os.path import expanduser
from subprocess import Popen

# Fast bytes convertion
def byt(text):
	return bytes(text, "utf-8")

# Waits for new connections
def accept_connection():
	global IPS
	global connections
	global QUIT

	try:
		while(not QUIT):
			client, client_address = s.accept()
			print(str(client_address) + " has connected.")
			client.send(byt("Connected\n"))
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

# Server activities
def handle_client(client, IP):
	'''

	Commands:

	0 = show_topics()
	1 = in(Remove postagem)
	2 = rd(Lê postagem)
	3 = out(Adiciona postagem)

	'''

	client.send(byt("Type a username"))
	username = client.recv(4096).decode()

	client.send(byt("\nCommands:\n\nshow\nwrite <topic> <msg>\nread <topic> <page_num=0>\ndelete <topic>\nquit\nh(elp)\n"))

	if(True):
	#try:
		while(True):
			data = client.recv(4096).decode()
			command = data.split(" ")[0]
				
			# Temporary halt
			if(command == "show"):
				client.send(byt(show_topics()))
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
				client.send(byt("\n\nCommands:\n\nshow\nwrite <topic> <msg>\nread <topic> <page_num=0>\ndelete <topic>\nquit\nh(elp)\n"))
				continue


	'''			
	except:
		client.send(byt("Quit"))
		return
	'''


IPS = []
connections = {}
POSTDIR = os.getcwd() + "\\Blogs\\"
HOST = '186.219.90.134'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
QUIT = False

if(not os.path.exists(POSTDIR)):
	os.system("mkdir Blogs")

s = socket(AF_INET, SOCK_STREAM) 
s.bind((HOST, PORT))  
s.listen(1)           
accept_connection()