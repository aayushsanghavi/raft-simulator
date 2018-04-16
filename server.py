from variables import *
from leader import Leader
from follower import Follower
from message import Message

class Server():
    def __init__(self, name, state, log, neighbors):
        self.X = 0
        self._name = name
        self._state = state
        self._log = log
        self._board = []
        self._neighbors = neighbors
        self._total_nodes = 0
        self._commitIndex = -1
        self._currentTerm = 0
        self._lastApplied = 0
        self._lastLogIndex = -1
        self._lastLogTerm = None
        self._serverState = followerState
        self._state.set_server(self)

    def post_message(self, message):
        self._board.append(message)
        self._board = sorted(self._board, key=lambda a: a.timestamp, reverse=True)

    def get_message(self):
        if len(self._board) > 0:
            return self._board.pop()
        else:
            return None

    def send_message(self, message):
        for n in self._neighbors:
            if n._serverState != deadState:
                message._receiver = n._name
                n.post_message(message)

    def send_message_response(self, message):
        for n in self._neighbors:
            if n._name == message.receiver:
                n.post_message(message)

    def on_message(self, message):
        if (message._type == Message.RequestVoteResponse or message._type == Message.RequestVote) and type(self._state) == Leader:
            return
        if (message._type == Message.RequestVoteResponse) and type(self._state) == Follower:
            return
        state, response = self._state.on_message(message)
        if type(state) == Leader and type(self._state) != Leader:
            self._state = state
            self._state._send_heart_beat()
        self._state = state

    def on_client_command(self, message_data):
        """This is called when there is a client request."""
        leader = None
        leaderTerm = None
        for n in self._neighbors:
            if type(n._state) == Leader:
                leader = n._name
                leaderTerm = n._currentTerm
        message = Message(self._name, leader, leaderTerm, {
            "command": message_data,
        }, Message.ClientCommand)
        if leader != None:
            self.send_message_response(message)
        else:
            self._state.run_client_command(message)
