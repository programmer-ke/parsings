"""A minimal scanner/tokenizer"""

from dataclasses import dataclass
import re


TOKEN_SPEC = [
    (r"^def\b", "DEF"),
    (r"^[a-zA-Z_][a-zA-Z0-9_]*", "NAME"),
    (r"^[0-9]+", "INTEGER"),
    (r"^\(", "LPAREN"),
    (r"^\)", "RPAREN"),
    (r"^\+", "PLUS"),
    (r"^:", "COLON"),
    (r"^,", "COMMA"),
]


@dataclass
class Token:
    name: str
    matched_text: str
    end_column: int
    length: int


class Scanner:
    def __init__(self, token_spec):
        self._token_spec = [(re.compile(pattern), name) for pattern, name in token_spec]
        self._matched_tokens = []

    def has_tokens(self):
        return len(self._matched_tokens) > 0

    def scan(self, text: list[str]) -> None:
        """Parses text into a list of tokens"""

        for line in text:
            start_index = 0
            while start_index < len(line):
                if line[start_index].isspace():
                    start_index += 1
                    continue
                token = self._get_next_match(line, start_index)
                if not token:
                    raise SyntaxError(f"No token matched: {line[start_index:]}")
                self._matched_tokens.append(token)
                start_index += token.length

    def _get_next_match(self, line: str, start_index: int) -> Token | None:
        """Returns the next matched token from line"""

        segment = line[start_index:]

        for pattern, token_name in self._token_spec:
            if possible_match := pattern.match(segment):
                match_end = possible_match.end()
                return Token(
                    name=token_name,
                    matched_text=segment[:match_end],
                    end_column=start_index + match_end,
                    length=match_end,
                )
        return None

    def match(self, token_types):
        """Consumes and returns first token if in token_types"""
        if not self._matched_tokens or not token_types:
            return None

        if self._matched_tokens[0].name in token_types:
            return self._matched_tokens.pop(0)
        return None

    def peek(self, token_types=None):
        """Returns first token without consuming it

        If token_types is given, return first token only if it matches"""

        if not self._matched_tokens:
            return None

        first = self._matched_tokens[0]
        if not token_types:
            return first
        elif first.name in token_types:
            return first
        return None

    def push(self, token):
        """Pushes a token back to the head of the token stream"""

        if token:
            self._matched_tokens.insert(0, token)
