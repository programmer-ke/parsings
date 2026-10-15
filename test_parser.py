from scanner import Scanner
from parser import PyParser
import pytest

TOKEN_SPEC = [
    (r"^def", "DEF"),
    (r"^[a-zA-Z_][a-zA-Z0-9_]*", "NAME"),
    (r"^[0-9]+", "INTEGER"),
    (r"^\(", "LPAREN"),
    (r"^\)", "RPAREN"),
    (r"^\+", "PLUS"),
    (r"^:", "COLON"),
    (r"^,", "COMMA"),
]


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
