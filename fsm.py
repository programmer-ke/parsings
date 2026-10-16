"""FSM simulating network server"""


def START():
    return LISTENING


def LISTENING(event):
    if event == "error":
        return LISTENING
    elif event == "connect":
        return CONNECTED
    else:
        return ERROR


def CONNECTED(event):
    if event == "accept":
        return ACCEPTED
    elif event == "close":
        return CLOSED
    else:
        return ERROR


def ACCEPTED(event):
    if event == "close":
        return CLOSED
    elif event == "write":
        return WRITING(event)
    elif event == "read":
        return READING(event)
    else:
        return ERROR


def WRITING(event):
    if event == "write":
        return WRITING
    elif event == "read":
        return READING(event)
    elif event == "close":
        return CLOSED
    else:
        return ERROR


def READING(event):
    if event == "read":
        return READING
    elif event == "write":
        return WRITING(event)
    elif event == "close":
        return CLOSED
    else:
        return ERROR


def CLOSED(event):
    return LISTENING(event)


def ERROR(event):
    return ERROR
