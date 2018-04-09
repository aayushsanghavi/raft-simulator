from collections import defaultdict
from state import State
from message import Message

class Leader(State):
    def __init__(self):
        self._nextIndexes = defaultdict(int)
        self._matchIndex = defaultdict(int)

    def set_server(self, server):
        self._server = server

        for n in self._server._neighbors:
            self._nextIndexes[n._name] = self._server._lastLogIndex + 1
            self._matchIndex[n._name] = 0

    def run_client_command(self, message):
        term = self._server._currentTerm
        value = message._data["command"]
        log = {"term": term, "value": value}
        self._server._lastLogIndex = max(len(self._server._log) - 1, 0)
        self._server._log.append(log)
        self._server._lastLogTerm = term

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
        # Was the last AppendEntries good?
        if not message.data["response"]:
            # No, so lets back up the log for this node
            self._nextIndexes[message.sender] -= 1

            # Get the next log entry to send to the client.
            previousIndex = max(0, self._nextIndexes[message.sender] - 1)
            previous = self._server._log[previousIndex]
            current = self._server._log[self._nextIndexes[message.sender]]

            # Send the new log to the client and wait for it to respond.
            appendEntry = Message(
                self._server._name,
                message.sender,
                self._server._currentTerm,
                {
                    "leaderId": self._server._name,
                    "prevLogIndex": previousIndex,
                    "prevLogTerm": previous["term"],
                    "entries": [current],
                    "leaderCommit": self._server._commitIndex,
                }, Message.AppendEntries)

            self._send_response_message(appendEntry)
        else:
            # The last append was good so increase their index.
            self._nextIndexes[message.sender] += 1

            # Are they caught up?
            if self._nextIndexes[message.sender] > self._server._lastLogIndex:
                self._nextIndexes[message.sender] = self._server._lastLogIndex

        return self, None

    def _send_heart_beat(self):
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
