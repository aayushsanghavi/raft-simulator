import time
from variables import *
from voter import Voter
from leader import Leader
from message import Message

class Candidate(Voter):
    def set_server(self, server):
        self._server = server
        self._votes = {}
        self._start_election()

    def on_vote_request(self, message):
        return self, None

    def on_vote_received(self, message):
        self._votes[message.sender] = message

        print "Total nodes = ", self._server._total_nodes
        print "Total votes = ", len(self._votes.keys())

        if(len(self._votes.keys()) > (self._server._total_nodes - 1) / 2):
            leader = Leader()
            leader.set_server(self._server)
            print "Server", self._server._name, "has been elected leader"
            self._server._serverState = leaderState
            for n in self._server._neighbors:
                if n._serverState != deadState:
                    n._serverState = followerState
            return leader, None

        return self, None

    def _start_election(self):
        self._server._currentTerm += 1
        election = Message(
            self._server._name,
            None,
            self._server._currentTerm,
            {
                "lastLogIndex": self._server._lastLogIndex,
                "lastLogTerm": self._server._lastLogTerm,
            }, Message.RequestVote)

        self._server.send_message(election)
        self._last_vote = self._server._name
