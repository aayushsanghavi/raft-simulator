from state import State
from message import Message
from collections import defaultdict

class Leader(State):
    def __init__(self, timeout=0.5):
        self._timeout = timeout
        self._nextIndexes = defaultdict(int)
        self._matchIndex = defaultdict(int)
        self._ackCount = defaultdict(int)
        self._timeoutTime = self._nextTimeout()
        self._numofMessages = {}

    def set_server(self, server):
        self._server = server

        for n in self._server._neighbors:
            self._nextIndexes[n._name] = self._server._lastLogIndex + 1
            self._matchIndex[n._name] = 0

    def send_pending_messages(self, server):
        entries = []
        log = self._server._log
        if len(log) == 0:
            return
        self._nextIndexes[server] = len(log) - 1
        message = Message(
            self._server._name,
            server,
            self._server._currentTerm,
            {
                "leaderId": self._server._name,
                "prevLogIndex": len(log) - 2,
                "prevLogTerm": self._server._currentTerm,
                "entries": [log[-1]],
                "leaderCommit": self._server._commitIndex,
            }, Message.AppendEntries)
        self._server.send_message_response(message)

    def run_client_command(self, message):
        term = self._server._currentTerm
        value = message._data["command"]
        log = {"term": term, "value": value}
        self._server._lastLogIndex = len(self._server._log) - 1
        self._server._lastLogTerm = term
        if self._server._lastLogIndex > -1:
            self._server._lastLogTerm = self._server._log[self._server._lastLogIndex]
        self._server._log.append(log)
        for n in self._server._neighbors:
            self._numofMessages[n._name] = 1

        message = Message(
            self._server._name,
            None,
            self._server._currentTerm,
            {
                "leaderId": self._server._name,
                "prevLogIndex": self._server._lastLogIndex,
                "prevLogTerm": self._server._lastLogTerm,
                "entries": [log],
                "leaderCommit": self._server._commitIndex,
            }, Message.AppendEntries)
        self._server.send_message(message)
        return self, None

    def on_response_received(self, message):
        if not message.data["response"]:
            self._nextIndexes[message.sender] -= 1
            previousIndex = self._nextIndexes[message._sender] - 1
            previous = self._server._log[previousIndex]
            current = self._server._log[self._nextIndexes[message._sender]:]
            self._numofMessages[message._sender] = len(current)
            appendEntry = Message(
                self._server._name,
                message._sender,
                self._server._currentTerm,
                {
                    "leaderId": self._server._name,
                    "prevLogIndex": previousIndex,
                    "prevLogTerm": previous["term"],
                    "entries": current,
                    "leaderCommit": self._server._commitIndex,
                }, Message.AppendEntries)

            self._server.send_message_response(appendEntry)
        else:
            index = self._nextIndexes[message._sender]
            lastIndex = index + self._numofMessages[message._sender] - 1
            self._nextIndexes[message._sender] += self._numofMessages[message._sender]
            print "index", index, self._ackCount[index]

            for i in range(lastIndex, index-1, -1):
                self._ackCount[i] += 1
                if self._ackCount[i] == (self._server._total_nodes + 1) / 2:
                    if i > self._server._commitIndex:
                        for j in range(self._server._commitIndex+1, i+1):
                            self._server._x += int(self._server._log[j]["value"])
                        self._server._commitIndex = i
                    print "committed", self._server._commitIndex
                    break

        return self, None

    def _send_heart_beat(self):
        self._timeoutTime = self._nextTimeout()
        self._server._lastLogIndex = len(self._server._log) - 1
        message = Message(
            self._server._name,
            None,
            self._server._currentTerm,
            {
                "leaderId": self._server._name,
                "prevLogIndex": self._server._lastLogIndex,
                "prevLogTerm": self._server._lastLogTerm,
                "entries": [],
                "leaderCommit": self._server._commitIndex,
            }, Message.AppendEntries)
        self._server.send_message(message)
