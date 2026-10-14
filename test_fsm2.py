import fsm2

def test_basic_connection():
    state = fsm2.Connection()
    script = ["connect", "accept", "read", "write", "close", "connect"]

    for event in script:
        print(event, ">>>", state)
        getattr(state, event)()

if __name__ == "__main__":
    test_basic_connection()
