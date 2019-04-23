from socket  import *
from threading import Thread
import os
from os.path import expanduser
from subprocess import Popen
from threading import Thread
from datetime import datetime
from time import sleep

# Fast bytes convertion
def byt(text):
	return bytes(text, "utf-8")

# Checks if serial is in awaited connections
def authenticate(text):
	global Auths

	for i in range(0,5):
		if(not text in Auths):
			sleep(0.8)
		else:
			Auths.remove(text)
			return True
	return False

# See if two characters are at least 4 ASCII distant from each other
def in_range(a,b):
	rang = ord(a) - ord(b)

	if(rang < -3 or rang > 3):
		return False
	else:
		return True

# Checks if serial is valid
def verify_auth(text):
	file = open(CLIENTDIR + "client.py", "r")
	data = file.read()
	file.close()
	if(len(text) == int(len(data)/4)):
		for i in range(0, int(len(text)/4)):
			if(not in_range(text[i], data[i*4])):
				return False
		return True
	else:
		return False

# Waits for new connections
def accept_connection():
	global IPS
	global connections
	global QUIT
	global clients

	Auth_Conn = Thread(target=accept_auth_server_connection)
	Auth_Conn.start()

	try:
		while(not QUIT):
			client, client_address = s.accept()
			if(not authenticate(client.recv(4096).decode())):
				client.send(byt("<AuthF>"))
				continue

			print(str(client_address) + " has connected.")
			client.send(byt("Connected\n"))
			clients[client] = [0, ""]
			IPS.append(client_address)
			connections[client_address] = Thread(target=handle_client, args=(client,client_address))
			connections[client_address].start()
	except KeyboardInterrupt:
		exit()

# Waits for connection from Auth Server
def accept_auth_server_connection():
	global Auths

	auth_server, auth_address = auth_s.accept()	
	print("Authentication Server Connected!")
	while(not QUIT):
		try:
			code = auth_server.recv(4096).decode()
			if(verify_auth(code)):
				Auths.append(code)
			else:
				print("Blocked a malicious authentication code!")
		except:
			print("Authentication Server connection error!")
			return


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
def help_message(name):
	if(not is_admin(name)):
		return "Commands:\n\n------ Blog ------\n\nposts\nwrite <topic> <msg>\nread <topic> <page_num=0>\ndelete <topic>\n\n------ Files ------\n\nupload <filedir>\nfiles\ndownload <file>\n\n------ Miscellaneous ------\n\nchat\nquit\nh(elp)\n"
	else:
		return "Commands:\n\n------ Blog ------\n\nposts\nwrite <topic> <msg>\nread <topic> <page_num=0>\ndelete <topic>\n\n------ Files ------\n\nupload <filedir>\nfiles\ndownload <file>\n\n------ Miscellaneous ------\n\nchat\nquit\nh(elp)\n\n------ Admin ------\n\nwho\ndelete_post <post>\ndelete_file <filename>\ncrash\n"

# Prints all online users in chat
def whoson():
	global clients
	acc = "Online Users: \n\n"

	for sock in clients:
		if(clients[sock][0] == 1):
			acc += clients[sock][1] + "\n"

	return acc

# Print chat help message
def print_chat_help(name):
	if(not is_admin(name)):
		return "Type /q to quit\n/w to see who's online\n/c to clear chat windows\n"
	else:
		return "Type /q to quit\n/w to see who's online\n/c to clear chat windows\n/k <user> to kick user from chat\n"


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

# Log in or creates an account
def account_management(client):
	client.send(byt("/l <username> <password> to login\n/c <username> <password> to create an account\n/q quit\n"))
	err = False

	while(True):
		data = client.recv(4096).decode()

		if(data[0:2] == "/q"):
			return "-1", False

		username = data.split(" ")[1]
		password = data.split(" ")[2]
		if(data[0:2] == "/l"):
			return login(client, username, password)
		elif(data[0:2] == "/c"):
			err = create_account(client, username, password)
			sleep(1)
			if(err):
				return "-1", False
			client.send(byt("Account " + username + " created successfully\n"))
			return account_management(client)


# Checks for an account info
def login(client, username, password):
	ADMIN = False
	file = open(ACCFILE, "rb")
	f_data = file.read().decode().split("\n")
	file.close()

	if(username[-3:] == "<A>"):
		username = username[:-3]

	for line in f_data:
		if(username == line.split("\t")[0]):
			if(password == line.split("\t")[1]):
				if(line.split("\t")[2] == "Admin"):
					ADMIN = True
				return username, ADMIN
			client.send(byt("Wrong password for account: " + username + "\n"))
			return account_management(client)
	client.send(byt("No account registered as: " + username + "\n"))
	return account_management(client)

# Creates a new account and saves to _ref file
def create_account(client, username, password):
	ADMIN = False
	if(username[-3:] == "<A>"):
		name = username[:-3]
		ADMIN = True
	else:
		name = username

	# Existence check
	file = open(ACCFILE, "rb")
	f_data = file.read().decode().split("\n")
	file.close()

	for line in f_data:
		if(name == line.split("\t")[0]):
			client.send(byt("Account already exists\n"))
			sleep(1)
			return True
				

	file = open(ACCFILE, "ab")
	if(ADMIN):
		file.write(byt(name + "\t" + password + "\t" + "Admin\n"))
	else:
		file.write(byt(name + "\t" + password + "\t" + "User\n"))
	file.close()	
	return False

# Admin query for admin commands
def admin_query(client, command):
	# General who's on
	# Delete file
	# Delete post
	# Kick from chat (in chat)
	# Crash all users

	com = command.split(" ")[0]
	try:
		tgt = command.split(" ")[1]
	except:
		tgt = ""

	global clients

	if(com == "who"):
		who = []
		i = 0
		for key in clients:
			who.append(clients[key][1] + "\n")
			i += 1
		client.send(byt("".join(who) + "\n\nOnline: " + str(i) + "\n"))
		return

	elif(com == "delete_file"):
		if(check_file(tgt)):
			update_file(tgt)
			os.remove(FILEDIR + tgt)
			client.send(byt(tgt + " deleted!\n"))
			return
		else:
			client.send(byt("File not Found\n"))
			return

	elif(com == "delete_post"):
		if(os.path.isfile(POSTDIR + tgt + ".txt")):	
			os.remove(POSTDIR + tgt + ".txt")
			client.send(byt(tgt + " deleted!\n"))
			return	
		else:
			client.send(byt("File not Found\n"))
			return

	elif(com == "crash"):
		pops = []
		for key in clients:
			if(not is_admin(clients[key][1])):
				key.send(byt("Quit"))
				pops.append(key)
				print(str(key) + " crashed.")
		for con in pops:
			clients.pop(con)
		client.send(byt("Crashed all Users' connection"))
		return

# Checks if an username is Admin
def is_admin(name):
	file = open(ACCFILE, "r")
	file_data = file.readlines()
	file.close()

	for line in file_data:
		if(name == line.split("\t")[0]):
			if(line.split("\t")[2] == "Admin\n"):
				return True
	return False

# returns client key for user
def get_user_connection(username):
	for key in clients:
		if(clients[key][1] == username):
			return key

# Server activities
def handle_client(client, IP):
	message_count = 0  # After 20 messages, show help message
	CHAT = 0
	FTP = False
	FTP_out = False
	file_data = b''
	ADMIN = False

	username, ADMIN = account_management(client)

	if(username == "-1" and not ADMIN):
		client.send(byt("Quit"))
		print(str(IP) + " disconnected\n")
		return

	global clients
	clients[client] = [0, username]
	print(username + " anthenticated")

	client.send(byt(help_message(username)))

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
				if(data[0:2] == "/k" and is_admin(username)):
					try:
						tgt = data.split(" ")[1]
					except:
						client.send(byt("Syntax: /k <user>\n"))
						continue

					tgt_con = get_user_connection(tgt)

					if(tgt_con == None):
						client.send(byt("User " + tgt + " doesn't exist"))
						continue

					clients[tgt_con] = [0, tgt]
					tgt_con.send(byt("You have been kicked from Chat\n\n/q to go back\n"))
					broadcast(tgt + " has been kicked by " + username + "\n", username)
					client.send(byt(tgt + " has been kicked by " + username + "\n"))
					continue

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
						client.send(byt(print_chat_help(username)))
						message_count = 0
				continue

			if(command == "posts"):
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
			elif(command == "h" or command == "help"):
				client.send(byt(help_message(username)))
				continue
			elif(is_admin(username)):
				admin_query(client, data)
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
ACCOUNTDIR = os.getcwd() + "\\Accounts\\"
CLIENTDIR = os.getcwd() + "\\Updated_Client\\"
ACCFILE = ACCOUNTDIR + "_ref"
HOST = "200.136.205.254" # "177.183.170.34"
PORT = 33000
AUTH_PORT = 33002
BUFSIZ = 1024
QUIT = False
Chat_Threads = []
Auths = []

if(not os.path.exists(CLIENTDIR)):
	os.system("mkdir Updated_Client")

if(not os.path.exists(POSTDIR)):
	os.system("mkdir Blogs")

if(not os.path.exists(FILEDIR)):
	os.system("mkdir Files")
if(not os.path.isfile(REFFILE)):
	reffile = open(FILEDIR + "_ref", "w")
	reffile.close()

if(not os.path.exists(ACCOUNTDIR)):
	os.system("mkdir Accounts")
if(not os.path.isfile(ACCFILE)):
	reffile = open(ACCFILE, "w")
	reffile.close()


s = socket(AF_INET, SOCK_STREAM) 
s.bind((HOST, PORT))  
s.listen(1)     

auth_s = socket(AF_INET, SOCK_STREAM) 
auth_s.bind((HOST, AUTH_PORT))  
auth_s.listen(1) 

accept_connection()