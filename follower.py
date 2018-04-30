from voter import Voter
from leader import Leader

class Follower(Voter):
    def __init__(self, timeout=1):
        Voter.__init__(self)
        self._timeout = timeout
        self._timeoutTime = self._nextTimeout()

    def on_resume(self):
        leader = None
        for n in self._server._neighbors:
            if type(n._state) == Leader:
                leader = n
        leader._state.send_pending_messages(self._server._name)

    def on_append_entries(self, message):
        for j in range(self._server._commitIndex+1, min(message._data["leaderCommit"]+1, len(self._server._log))):
            self._server._x += int(self._server._log[j]["value"])

        self._server._commitIndex = min(message._data["leaderCommit"], len(self._server._log)-1)
        print message._data
        print self._server._x
        self._timeoutTime = self._nextTimeout()

        if message._term < self._server._currentTerm:
            self._send_response_message(message, yes=False)
            return self, None

        if message._data != {}:
            log = self._server._log
            data = message._data
            if data["prevLogIndex"] > -1 and len(log) <= data["prevLogIndex"]:
                self._send_response_message(message, yes=False)
                return self, None

            if len(log) > 0 and log[data["prevLogIndex"]]["term"] != data["prevLogTerm"]:
                log = log[:data["prevLogIndex"]]
                self._send_response_message(message, yes=False)
                self._server._log = log
                self._server._lastLogIndex = data["prevLogIndex"]
                self._server._lastLogTerm = data["prevLogTerm"]
                return self, None
            else:
                if len(data["entries"]) > 0:
                    for e in data["entries"]:
                        log.append(e)                        
                    print log

                    self._server._lastLogIndex = len(log) - 1
                    self._server._lastLogTerm = log[-1]["term"]
                    self._server._log = log
                    self._send_response_message(message)

            return self, None
        else:
            return self, None
