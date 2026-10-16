from scanner import Scanner, TOKEN_SPEC
from parser import PyParser
import pytest


def test_parser():
    scanner = Scanner(TOKEN_SPEC)
    code = [
        "def print_sum(x, y):",
        "    print(x + y)",
        "print_sum(10, 20)",
    ]
    scanner.scan(code)
    parser = PyParser(scanner)
    print("parsing..")
    parser.parse()
    print("parsed..")
    parser.show()
