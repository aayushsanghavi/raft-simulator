import time
from server import Server
from follower import Follower
from threading import Thread
from message import Message
from memory_board import MemoryBoard

config = {}
available_id = 0
term = 0

def myfunction(name):
	if config[name]["alive"] == 1:
		print "Started server with name ", name
	elif config[name]["alive"] == 2:
		print "Resumed server with name ", name
		for message in config[name]["object"]._messageBoard._board:
			print message._data
		config[name]["alive"] = 1

	while(True):
		if config[name]["alive"] == 0:
			print "Killed server with name ", name
			return

print "1. Start a new server"
print "2. Kill a server: name"
print "3. Resume a server: name"
print "4. Send a message: sender receiver message"

while(True):
	command = raw_input()
	args = command.split()
	if args[0] == "1":
		board = MemoryBoard()
		state = Follower()
		server = Server(available_id, state, [], board, [])
		thread = Thread(target=myfunction, args=(available_id,))
		config[available_id] = {"object": server, "alive": 1}
		available_id += 1
		thread.start()
	elif args[0] == "2":
		name = int(args[1])
		config[name]["alive"] = 0
	elif args[0] == "3":
		name = int(args[1])
		config[name]["alive"] = 2
		thread = Thread(target=myfunction, args=(name,))
		thread.start()
	elif args[0] == "4":
		sender = int(args[1])
		receiver = int(args[2])
		message_data = args[3]
		if config[sender]["alive"] and config[receiver]["alive"]:
			message = Message(sender, receiver, term, message_data, Message.AppendEntries)
			config[receiver]["object"].post_message(message)
