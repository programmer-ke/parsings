"""A minimal scanner/tokenizer"""

from dataclasses import dataclass
import re


@dataclass
class Token:
    name: str
    matched_text: str
    line_index: int
    length: int


class Scanner:
    def __init__(self, token_spec):
        self._token_spec = [(re.compile(pattern), name) for pattern, name in token_spec]
        self._matched_tokens = []

    def scan(self, text: list[str]) -> None:
        """Parses text into a list of tokens"""

        for line in text:
            start_index = 0
            while start_index < len(line):
                token = self._get_next_match(line, start_index)
                if not token:
                    raise SyntaxError(f"No token matched: {line[start_index:]}")
                self._matched_tokens.append(token)
                start_index += token.length

    def _get_next_match(self, line: str, start_index: int) -> Token | None:
        """Returns the next matched token from line"""

        for pattern, token_name in self._token_spec:
            segment = line[start_index:]
            if possible_match := pattern.match(segment):
                match_end = possible_match.end()
                return Token(
                    name=token_name,
                    matched_text=segment[:match_end],
                    line_index=start_index + match_end,
                    length=match_end,
                )

    def match(self, token_types):
        """Consumes and returns first token if in token_types"""
        ...

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
        ...
