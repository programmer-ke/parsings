import fsm3
import sys


def test_basic_connection():
    conn = fsm3.Connection()
    script = ["connect", "accept", "read", "write", "close", "connect"]

    for event in script * 2:
        print(event, ">>>", conn._state)
        getattr(conn, event)()


def profile():
    orig = sys.stdout
    sys.stdout = open("/dev/null", "w")

    conn = fsm3.Connection()
    script = ["connect", "accept", "read", "write", "close", "connect"]

    count = 1000 * 10
    while count > 0:
        for event in script:
            getattr(conn, event)()
        count -= 1

    sys.stdout.close()
    sys.stdout = orig


if __name__ == "__main__":
    profile()
