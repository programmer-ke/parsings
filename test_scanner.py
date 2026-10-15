import re
from scanner import Scanner, Token
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
    (r"^\s+", "INDENT"),
]


def test_token_spec():
    scanner = Scanner(TOKEN_SPEC)
    [(pattern, name), *_] = TOKEN_SPEC
    first, *rest = scanner._token_spec
    assert first == (re.compile(pattern), name)


def test_scanning_success():
    code = [
        "def hello(x, y):",
        "    print(x + y)",
        "hello(10, 20)",
    ]

    expected_output = [
        ("DEF", "def", 3, 3),
        ("INDENT", " ", 4, 1),
        ("NAME", "hello", 9, 5),
        ("LPAREN", "(", 10, 1),
        ("NAME", "x", 11, 1),
        ("COMMA", ",", 12, 1),
        ("INDENT", " ", 13, 1),
        ("NAME", "y", 14, 1),
        ("RPAREN", ")", 15, 1),
        ("COLON", ":", 16, 1),
        ("INDENT", "    ", 4, 4),
        ("NAME", "print", 9, 5),
        ("LPAREN", "(", 10, 1),
        ("NAME", "x", 11, 1),
        ("INDENT", " ", 12, 1),
        ("PLUS", "+", 13, 1),
        ("INDENT", " ", 14, 1),
        ("NAME", "y", 15, 1),
        ("RPAREN", ")", 16, 1),
        ("NAME", "hello", 5, 5),
        ("LPAREN", "(", 6, 1),
        ("INTEGER", "10", 8, 2),
        ("COMMA", ",", 9, 1),
        ("INDENT", " ", 10, 1),
        ("INTEGER", "20", 12, 2),
        ("RPAREN", ")", 13, 1),
    ]

    expected_output = [Token(*t) for t in expected_output]

    scanner = Scanner(TOKEN_SPEC)
    scanner.scan(code)
    assert scanner._matched_tokens == expected_output

    # test peek without token types
    first = scanner.peek()
    assert (first.name, first.matched_text) == ("DEF", "def")

    # test peek with token types
    first = scanner.peek(["DEF"])
    assert (first.name, first.matched_text) == ("DEF", "def")

    first = scanner.peek(["LPAREN"])
    assert first is None

    # test match, returns None with non-matching token
    token = scanner.match(["LPAREN"])
    assert token is None

    # test match with matching token
    token = scanner.match(["LPAREN", "DEF"])
    assert token.name == "DEF"

    # should have advanced
    assert scanner.peek().name == "INDENT"

    # test push back token
    scanner.push(token)
    assert scanner.peek().name == "DEF"


def test_scanning_failure():
    input_lines = ["***"]
    scanner = Scanner(TOKEN_SPEC)
    with pytest.raises(SyntaxError):
        scanner.scan(input_lines)
