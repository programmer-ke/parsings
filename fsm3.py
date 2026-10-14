"""FSM simulating network server, loosely based on the state design pattern

Connection delegates actions to state handlers
"""


class Connection:

    def __init__(self):
        self._new_state(Listening)

    def _new_state(self, state):
        self._state = state

    def error(self):
        self._state.error(self)

    def connect(self):
        self._state.connect(self)

    def accept(self):
        self._state.accept(self)

    def close(self):
        self._state.close(self)

    def write(self):
        self._state.write(self)

    def read(self):
        self._state.read(self)


class State:
    @classmethod
    def error(cls, conn):
        cls.default_action(conn)

    @classmethod
    def connect(cls, conn):
        cls.default_action(conn)

    @classmethod
    def accept(cls, conn):
        cls.default_action(conn)

    @classmethod
    def close(cls, conn):
        cls.default_action(conn)

    @classmethod
    def write(cls, conn):
        cls.default_action(conn)

    @classmethod
    def read(cls, conn):
        cls.default_action(conn)

    @staticmethod
    def default_action(conn):
        conn._new_state(Errored)


class Listening(State):
    @staticmethod
    def error(conn):
        pass

    @staticmethod
    def connect(conn):
        conn._new_state(Open)


class Open(State):
    @staticmethod
    def accept(conn):
        conn._new_state(Accepted)

    @staticmethod
    def close(conn):
        conn._new_state(Closed)


class Accepted(State):
    @staticmethod
    def close(conn):
        conn._new_state(Closed)

    @staticmethod
    def write(conn):
        conn._new_state(Writing)
        conn.write()

    @staticmethod
    def read(conn):
        conn._new_state(Reading)
        conn.read()


class Writing(State):
    @staticmethod
    def write(conn):
        print("writing..")

    @staticmethod
    def read(conn):
        conn._new_state(Reading)
        conn.read()

    @staticmethod
    def close(conn):
        conn._new_state(Closed)


class Reading(State):
    @staticmethod
    def read(conn):
        print("reading...")

    @staticmethod
    def write(conn):
        conn._new_state(Writing)
        conn.write()

    @staticmethod
    def close(conn):
        conn._new_state(Closed)


class Closed(State):
    @staticmethod
    def default_action(conn):
        conn._new_state(Listening)


class Errored(State):
    pass
