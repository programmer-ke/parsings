"""FSM simulating network server, loosely based on the state design pattern"""

class Connection:

    def __init__(self):
        self._new_state(Listening)

    def _new_state(self, state):
        self.__class__ = state

    def error(self):
        self._default()

    def connect(self):
        self._default()

    def accept(self):
        self._default()

    def close(self):
        self._default()

    def write(self):
        self._default()

    def read(self):
        self._default()

    def _default(self):
        self._new_state(Errored)

class Listening(Connection):
    def error(self):
        pass

    def connect(self):
        self._new_state(Open)


class Open(Connection):
    def accept(self):
        self._new_state(Accepted)

    def close(self):
        self._new_state(Closed)

class Accepted(Connection):
    def close(self):
        self._new_state(Closed)

    def write(self):
        self._new_state(Writing)
        self.write()

    def read(self):
        self._new_state(Reading)
        self.read()

class Writing(Connection):
    def write(self):
        print("writing..")

    def read(self):
        self._new_state(Reading)
        self.read()

    def close(self):
        self._new_state(Closed)

class Reading(Connection):
    def read(self):
        print('reading...')

    def write(self):
        self._new_state(Writing)
        self.write()

    def close(self):
        self._new_state(Closed)

class Closed(Connection):
    def _default(self):
        self._new_state(Listening)

class Errored(Connection):
    pass
