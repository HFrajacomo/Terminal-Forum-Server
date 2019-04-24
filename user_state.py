from colorama import Fore, Style, init
from random import randint, choice

class user_state:
	chat = 0
	username = ""
	user_os = ""
	chat_color = ""


	def __init__(self, chat_state, username, user_os, chat_color):
		self.chat = chat_state
		self.username = username
		self.user_os = user_os
		self.chat_color = chat_color

	def __getitem__(self, i):
		if(i == 0):
			return self.chat
		elif(i == 1):
			return self.username
		elif(i == 2):
			return self.user_os
		elif(i == 3):
			return self.chat_color

	def __setitem__(self, i, value):
		if(i == 0):
			self.chat = value
		elif(i == 1):
			self.username = value
		elif(i == 2):
			self.user_os = value
		elif(i == 3):
			self.chat_color = value


def random_color():
	colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
	return choice(colors)
