from socket  import *
from threading import Thread, Event
import os
from os.path import expanduser
from subprocess import Popen
from threading import Thread
from datetime import datetime
from time import sleep
from platform import system
from user_state import *
from FTP import *
import re

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

# Filters tags in text
def filter_tag(text):
	return re.sub(r'<\w*>', "***", text)

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
	data = data.replace("\t", "")
	data = data.replace("\n", "")
	data = data.replace(" ", "")
	data = data.replace("\r", "")

	if(len(text) == int(len(data)/4)):
		for i in range(0, int(len(text)/4)):
			if(not in_range(text[i], data[i*4])):
				print("Invalid Authentication char in position: " + str(i) + " -> " + text[i])
				return False
		return True
	else:
		print("Invalid size of Authentication code: " + str(len(text)) + " vs " + str(int(len(data)/4)))
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

			os = client.recv(4096).decode()
			print(str(client_address) + " has connected.")
			client.send(byt("Connected\n"))
			clients[client] = user_state(0, "", os, random_color(), False, False)
			IPS.append(client_address)
			connections[client_address] = Thread(target=handle_client, args=(client,client_address))
			connections[client_address].start()
	except KeyboardInterrupt:
		exit()

# Waits for connection from Auth Server
def accept_auth_server_connection():
	global Auths
	global auth_server_threads

	while(not QUIT):
		auth_server, auth_address = auth_s.accept()	
		auth_server_threads.append(Thread(target=handle_auth_server, args=(auth_server,)))
		auth_server_threads[-1].start()
		print("Authentication Server Connected!")


# Handles auth server communication
def handle_auth_server(auth_server):
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

	msg = re.sub(r'<\w*>', "***", msg)

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
		return "Type /q to quit\n/h for help\n/w to see who's online\n/c to clear chat windows\n/cc to change display text color\n"
	else:
		return "Type /q to quit\n/h for help\n/w to see who's online\n/c to clear chat windows\n/cc to change display text color\n/k <user> to kick user from chat\n"


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
	err = False

	while(True):
		client.send(byt("/l <username> <password> to login\n/c <username> <password> to create an account\n/q quit\n"))
		data = client.recv(4096).decode()
		filt_user = ""

		if(data[0:2] == "/q"):
			return "-1", False

		# Lexic Analysis
		try:
			username = data.split(" ")[1]
			password = data.split(" ")[2]
		except:
			client.send(byt("Syntax Error: Please notice whitespaces are mandatory"))
			continue

		if(filter_tag(username) != username):
			client.send(byt("Syntax Error: Do not use Tags in usernames"))
			continue

		if(len(data.split(" "))>3):
			client.send(byt("Syntax Error: Username and Passwords can't have whitespaces"))
			continue
		# End Lexic Analysis

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
		tgt = " ".join(command.split(" ")[1:])
	except:
		tgt = ""

	global clients

	if(com == "who"):
		who = []
		i = 0
		for key in clients:
			if(is_admin(clients[key][1])):
				who.append(clients[key][1] + "(Admin)\n")
			else:
				who.append(clients[key][1] + "\n")
			i += 1
		client.send(byt("".join(who) + "\nOnline: " + str(i) + "\n"))
		log_message(client, "checked who's online")
		return

	elif(com == "delete_file"):
		if(check_file(tgt)):
			update_file(tgt)
			os.remove(FILEDIR + tgt)
			client.send(byt(tgt + " deleted!\n"))
			log_message(client, "deleted file " + tgt)
			return
		else:
			client.send(byt("File not Found\n"))
			return

	elif(com == "delete_post"):
		if(os.path.isfile(POSTDIR + tgt + ".txt")):	
			os.remove(POSTDIR + tgt + ".txt")
			client.send(byt(tgt + " deleted!\n"))
			log_message(client, "deleted post " + tgt)
			return	
		else:
			client.send(byt("File not Found\n"))
			return

	elif(com == "crash"):
		pops = []
		for key in clients:
			if(not is_admin(clients[key][1] and clients[key][4] == False)):
				key.send(byt("Quit"))
				pops.append(key)
				print(str(key) + " crashed.")
		for con in pops:
			clients.pop(con)
		client.send(byt("Crashed all Users' connection safely"))
		log_message(client, "crashed users")
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

# Generate log messages
def log_message(client, text):
	print(clients[client][1] + " " + text)

# Gets folder name in a directory
def get_folder_name(text):
	if(clients[client][2] == "Windows"):
		return "".join(" ".join(text.split(" ")[1:]).split("\\")[-1])
	else:
		return " ".join(text.split(" ")[1:]).split("/")[-1]

# Folder Syncronization Service
def folder_sync_thread(client):
	global clients
	i = 1
	USER_FOLDER = SYNCDIR + clients[client][1] + "\\"
	sync_sleep_time = 2

	if(os.path.exists(USER_FOLDER)):
		if(not os.path.exists(USER_FOLDER + "_ref")):
			reffile = open(USER_FOLDER + "_ref", "w")
			reffile.close()
	else:
		os.system("mkdir " + USER_FOLDER)
		reffile = open(USER_FOLDER + "_ref", "w")
		reffile.close()		

	client.send(byt("Folder Syncronization is on"))

	if(1):
	#try:
		while(clients[client][5]):
			if(not os.path.exists(USER_FOLDER)):
				os.system("mkdir " + USER_FOLDER)

			folder_sync(client, USER_FOLDER)
			sleep(sync_sleep_time)

	#except:
		#client.send(byt("Something went wrong with the folder syncronization"))
	clients[client][5] = False
	client.send(byt("Folder Syncronization has turned off"))

# File Sync parse
def parse_sync_ref(usr_fld, client):
	parsed = []
	file = open(usr_fld + "_ref", "r")

	for line in file:
		parsed.append([line.split("\t")[0], int(line.split("\t")[1])])

	return parsed

# Finds the index of file descriptor
def find_file(lista, filename):
	for i in range(len(lista)):
		if(lista[i][0] == filename):
			return i
	return None

# Request and gets file changes
def folder_sync(client, inF):
	last_sync = parse_sync_ref(inF, client)
	f_size = 0
	last_files = [] # Only names
	ftp = FTP()
	file_list = ""

	for desc in last_sync:
		last_files.append(desc[0])

	client.send(byt("<REPO>"))

	# Retrieve file list

	while(True):
		buf = client.recv(4096).decode()
		if(buf == "<REPO>"):
			break
		elif(buf[-6:] == "<REPO>"):
			file_list += buf[0:-6]
			break
		file_list += buf

	if(file_list == "<RepError1>"):
		print(clients[client][1] + " got RepError1")
		client.send(byt("Something went wrong with folder syncronization"))
		return
	elif(file_list == "<RepDirError>"):
		client.send(byt("Invalid Repository Directory in config.cfg"))
		return

	names = file_list.split("\n")[:-1]

	EV[client].clear()

	# File Adding
	for n in names:
		if(n in last_files): # If is in file _ref
			last_files.remove(n)
			i = find_file(last_sync, n)
			if(os.path.getsize(inF + n) == last_sync[i]): # if size is the same
				pass
			else: # Not same size
				ftp.request_file(client, n)
				data = ftp.receive_file(client, tag="<FTPR>")
				file = open(inF + n, "wb")
				file.write(data)
				file.close()
				last_sync[i][1] = os.path.getsize(inF + n)

		else: # If new file
			ftp.request_file(client, n)
			data = ftp.receive_file(client, tag="<FTPR>")
			file = open(inF + n, "wb")
			file.write(data)
			file.close()			
			last_sync.append([n,os.path.getsize(inF + n)])

	EV[client].set()

	# File Removing
	for n in last_files:
		i = last_sync[find_file(last_sync, n)]
		if(i != None):
			os.remove(last_sync.pop(i)[0])

	# Updating _ref
	file = open("_ref", "w")
	for element in last_sync:
		file.write(element[0] + "\t" + str(element[1]) + "\n")

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

	global EV
	EV[client] = Event()
	EV[client].set()

	global clients
	clients[client][1] = username
	print(username + " anthenticated")

	client.send(byt(help_message(username)))

	if(True):
	#try:
		while(True):

			EV[client].wait()

			# To client FTP connection
			if(FTP_out):
				client.send(file.read())
				file.close()
				client.send(byt("<FTPin>"))
				log_message(client, "downloaded " + filename)
				FTP_out = False
				continue

			if(not FTP):
				data = client.recv(4096).decode()
				command = data.split(" ")[0]

			else: # Handle FTP Stream
				data = client.recv(4096)
				if(data[-5:] == byt("<FTP>")):
					file_data += data[0:-5]
					if(len(file_data) < 6):
						client.send(byt("File not Found"))
						log_message(client, "failed to upload " + filename)
						FTP = False
						file_data = b''
						continue

					if(check_file(filename)):
						update_file(filename)
					
					file = open(FILEDIR + filename, "wb")
					file.write(file_data)
					file.close()

					ref = open(REFFILE, "a")
					if(os.path.getsize(FILEDIR + filename) < 1048576):
						ref.write(filename + "\t" + username + "\t" + str(round(os.path.getsize(FILEDIR + filename)/1024, 1)) + " kB" + "\t" + str(datetime.now())[0:-7] + "\n")
					else:
						ref.write(filename + "\t" + username + "\t" + str(round(os.path.getsize(FILEDIR + filename)/1048576, 1)) + " MB" + "\t" + str(datetime.now())[0:-7] + "\n")
					ref.close()
					log_message(client, "uploaded " + filename)
					client.send(byt("File successfully sent"))
					FTP = False
					file_data = b''
					continue
				else:
					file_data += data
					continue


			# Turn on chat mode
			if(command == "chat" and CHAT == 0):
				clients[client][0] = 1
				client.send(byt("Connected to Chat!"))
				client.send(byt("<Color>"))
				client.send(byt(clients[client][3]))
				client.send(byt("<Color>"))
				log_message(client, "entered chat")
				broadcast(username + " has connected\n", username)
				client.send(byt(whoson()))
				CHAT = 1
				continue


			# Chat Mode
			elif(CHAT == 1):
				if(clients[client][0] == -1): # Kicked state
					if(data[0:2] == "/q"):
						client.send(byt("Disconnected from Chat!"))
						CHAT = 0
						message_count = 0
						clients[client][0] = 0
						continue
					else:
						continue				
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

					clients[tgt_con][0] = -1 
					log_message(client, "kicked " + clients[tgt_con][1] + " from chat")
					tgt_con.send(byt("You have been kicked from Chat\n\n/q to go back\n"))
					broadcast(tgt + " has been kicked by " + username + "\n", username)
					client.send(byt(tgt + " has been kicked by " + username + "\n"))
					continue

				if(data[0:2] == "/w"):
					client.send(byt(whoson()))
					continue
				if(data[0:2] == "/q"):
					client.send(byt("Disconnected from Chat!"))
					log_message(client, "left chat")
					CHAT = 0
					message_count = 0
					clients[client][0] = 0
					broadcast(username + " has disconnected\n", username)
					continue
				if(data[0:2] == "/h"):
					client.send(byt(print_chat_help(username)))
					message_count = 0
					continue
				if(data[0:3] == "/cc"):
					clients[client][3] = random_color()
					client.send(byt("<Color>"))
					client.send(byt(clients[client][3]))
					client.send(byt("<Color>"))
					continue
				else:
					message_count += 1
					t = datetime.now()
					msg = "|" + username + "|" + ": " + data + "\t[" + str(t.hour) + ":" + str(t.minute) + "]\n"
					msg = filter_tag(msg)
					broadcast(clients[client][3] + msg, username)

					if(message_count >= 20):
						client.send(byt(print_chat_help(username)))
						message_count = 0
				continue

			# See files in cloud repository
			if(command == "repo"):
				file = open(SYNCDIR + clients[client][1] + "\\" + "_ref", "r")
				client.send(byt(file.read()))
				file.close()
				continue

			elif(command == "sync"):
				if(clients[client][5]):
					clients[client][5] = False
					continue
				else:
					clients[client][5] = True
					file_sync_thread = Thread(target=folder_sync_thread, args=(client,))
					file_sync_thread.start()
					continue

			elif(command == "posts"):
				client.send(byt(show_topics()))
				continue

			# Activates FTP Stream
			elif(command == "upload"):
				try: #  Lexic Try
					if(clients[client][2] == "Windows"):
						filename = "".join(" ".join(data.split(" ")[1:]).split("\\")[-1])
					else:
						filename = " ".join(data.split(" ")[1:]).split("/")[-1]
				except:
					client.send(byt("Syntax: upload <filename>"))
					continue
				if(len(filename.replace(" ", "").replace("\n", "")) == 0):
					client.send(byt("Syntax: upload <filename>"))
					continue


				filed = " ".join(data.split(" ")[1:])
				FTP = True
				client.send(byt("<FTP>"))
				client.send(byt(filed))
				continue

			elif(command == "download"):
				filename = " ".join(data.split(" ")[1:])
				if(len(filename.replace(" ", "").replace("\n", "")) == 0):
					client.send(byt("Syntax: download <filename>"))
					continue
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
				try: # Lexic try
					topic = data.split(" ")[1]
					msg = " ".join(data.split(" ")[2:])
				except:
					client.send(byt("Syntax: write <topic> <message>"))
					continue
				if(topic == "" or msg == ""):
					client.send(byt("Syntax: write <topic> <message>"))
					continue					

				if(a_post(username, topic, msg)):
					log_message(client, "added to post " + topic)
					client.send(byt("Message successfully sent\n"))
				else:
					client.send(byt("There was a problem in your message\n"))
				continue
			elif(command == "read"):
				try: # Lexic try
					topic = data.split(" ")[1]
				except:
					client.send(byt("Syntax: read <topic> <pagenum?>"))
					continue

				try:
					page_num = int(data.split(" ")[2])
				except IndexError:
					page_num = 0
				client.send(byt(rd_post(topic, page_num)))
				log_message(client, "read " + topic)
				continue
			elif(command == "delete"):
				try: # Lexic try
					topic = data.split(" ")[1]
				except:
					client.send(byt("Syntax: delete <topic>"))
					continue

				if(rm_post(username, topic)):
					client.send(byt("Last message deleted\n"))
					log_message(client, "deleted their message at " + topic)
				else:
					client.send(byt("No user messages found\n"))
				continue
			elif(command == "quit"):
				client.send(byt("Quit"))
				print(str(IP) + " disconnected\n")
				clients.pop(client)
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

if(not os.path.isfile("ip.txt")):
	ipfile = open("ip.txt", "w")
	ipfile.write("IP=")
	ipfile.close()

IPS = []
connections = {}
clients = {}
auth_server_threads = []
POSTDIR = os.getcwd() + "\\Blogs\\"
FILEDIR = os.getcwd() + "\\Files\\"
SYNCDIR = os.getcwd() + "\\Sync\\"
REFFILE = FILEDIR + "_ref"
ACCOUNTDIR = os.getcwd() + "\\Accounts\\"
CLIENTDIR = os.getcwd() + "\\Updated_Client\\"
ACCFILE = ACCOUNTDIR + "_ref"
HOST = read_ip_file() # "192.168.0.13"
PORT = 33000
FTP_PORT = 33003
AUTH_PORT = 33002
BUFSIZ = 1024
QUIT = False
Chat_Threads = []
Auths = []
EV = {}

if(not os.path.exists(CLIENTDIR)):
	os.system("mkdir Updated_Client")

if(not os.path.exists(POSTDIR)):
	os.system("mkdir Blogs")

if(not os.path.exists(SYNCDIR)):
	os.system("mkdir Sync")

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

ftp_s = socket(AF_INET, SOCK_STREAM)
ftp_s.bind((HOST, FTP_PORT))
ftp_s.listen(1)

auth_s = socket(AF_INET, SOCK_STREAM) 
auth_s.bind((HOST, AUTH_PORT))  
auth_s.listen(1) 

accept_connection()