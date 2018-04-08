import time
from variables import *
from server import Server
from random import randint
from follower import Follower
from threading import Thread
from message import Message
from candidate import Candidate

term = 0
config = {}
available_id = 0

def checkMesages():
    while(True):
        time.sleep(0.01)
        for name in config:
            if config[name]["object"]._serverState != deadState:
                while(True):
                    message = config[name]["object"].get_message()
                    if message == None:
                        break
                    else:
                        config[name]["object"].on_message(message)

def serverFunction(name):
    if config[name]["object"]._serverState == followerState:
        print "Started server with name ", name
    elif config[name]["object"]._serverState == resumeState:
        print "Resumed server with name ", name
        for message in config[name]["object"]._board:
            print message._data
        config[name]["object"]._serverState = followerState

    while(True):
        if config[name]["object"]._serverState == deadState:
            print "Killed server with name ", name
            return
        if config[name]["object"]._serverState == candidateState and type(config[name]["object"]._state) != Candidate:
            timeout = randint(1.5e5, 3e5)
            timeout = 1.0*timeout/1e6
            time.sleep(timeout)
            if config[name]["object"]._serverState == candidateState:
                Server = config[name]["object"]
                Server._state = Candidate()
                Server._state.set_server(Server)

print "1. Start a new server"
print "2. Kill a server: name"
print "3. Resume a server: name"
print "4. Send a message: sender receiver message"
print "5. Initiate first election"

thread = Thread(target=checkMesages, args=())
thread.start()

while(True):
    command = raw_input()
    args = command.split()
    if args[0] == "1":
        state = Follower()
        server = Server(available_id, state, [], [])
        server._total_nodes = available_id + 1
        for i in range(available_id):
            server._neighbors.append(config[i]["object"])
            config[i]["object"]._total_nodes = available_id + 1
            config[i]["object"]._neighbors.append(server)

        thread = Thread(target=serverFunction, args=(available_id,))
        config[available_id] = {"object": server}
        available_id += 1
        thread.start()
    elif args[0] == "2":
        name = int(args[1])
        config[name]["object"]._serverState = deadState
    elif args[0] == "3":
        name = int(args[1])
        config[name]["object"]._serverState = resumeState
        thread = Thread(target=serverFunction, args=(name,))
        thread.start()
    elif args[0] == "4":
        sender = int(args[1])
        receiver = int(args[2])
        message_data = args[3]
        if config[sender]["object"]._serverState != deadState and config[receiver]["object"]._serverState != deadState:
            message = Message(sender, receiver, term, message_data, Message.AppendEntries)
            config[receiver]["object"].post_message(message)
    elif args[0] == "5":
        for i in range(available_id):
            if config[i]["object"]._serverState == followerState:
                config[i]["object"]._serverState = candidateState
