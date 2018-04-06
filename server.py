class Server():
    def __init__(self, name, state, log, neighbors):
        self._name = name
        self._state = state
        self._log = log
        self._board = []
        self._neighbors = neighbors
        self._total_nodes = 0
        self._commitIndex = 0
        self._currentTerm = 0
        self._lastApplied = 0
        self._lastLogIndex = 0
        self._lastLogTerm = None
        self._isAlive = True
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
            if n._isAlive:
                message._receiver = n._name
                n.post_message(message)
                message = n.get_message()
                print self._name, n._name, message._data
                n.on_message(message)

    def send_message_response(self, message):
        for n in self._neighbors:
            if n._name == message.receiver:
                n.post_message(message)
                print self._name, n._name, message._data
                n.on_message(n.get_message())

    def on_message(self, message):
        state, response = self._state.on_message(message)
        self._state = state
