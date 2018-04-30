from state import State
from message import Message

class Voter(State):
    def __init__(self):
        self._last_vote = {}

    def on_vote_request(self, message):
        if message._term not in self._last_vote and (message._data["lastLogTerm"], message._data["lastLogIndex"]) >= (self._server._lastLogTerm, self._server._lastLogIndex):
            print "OK"
            self._last_vote[message._term] = message.sender
            self._send_vote_response_message(message)
        else:
            self._send_vote_response_message(message, yes=False)
        return self, None

    def _send_vote_response_message(self, msg, yes=True):
        voteResponse = Message(
            self._server._name,
            msg.sender,
            msg.term,
            {"response": yes}, Message.RequestVoteResponse)
        self._server.send_message_response(voteResponse)
