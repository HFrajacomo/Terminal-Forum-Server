from socket import *

# Fast bytes convertion
def byt(text):
	return bytes(text, "utf-8")

class FTP:
	def __init__(self):
		pass

	# Server-side request
	def request_file(self, client, name):
		client.send(byt("<FTPR>"))
		client.send(byt(name))

	# Server-side receive
	def receive_file(self, client, tag="<EOF>"):
		downloaded = b''
		while(True):
			buf = client.recv(4096)
			if(buf == byt(tag)):
				break
			elif(buf[-len(tag):] == byt(tag)):
				downloaded += buf[0:-len(tag)]
				break
			downloaded += buf

		return downloaded

	# Server requests client repository files
	def request_repo(self, client):
		client.send(byt("<REP>"))

	# Client-side send
	def send_file(self, client, name):
		file = open(name, "rb")
		client.send(file.read())
		client.send(byt("<EOF>"))

