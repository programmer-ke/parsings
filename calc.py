import re
import abc
from collections import namedtuple
from dataclasses import dataclass

ASSIGN = r"(?P<ASSIGN>=)"
VARIABLE = r"(?P<VARIABLE>[a-zA-Z]+\w*)"
FLOAT = r"(?P<FLOAT>\d+\.\d*|\d*\.\d+)"
INTEGER = r"(?P<INTEGER>\d+)"
WHITESPACE = r"(?P<WHITESPACE>\s+)"
LPAREN = r"(?P<LPAREN>\()"
RPAREN = r"(?P<RPAREN>\))"
PLUS = r"(?P<PLUS>\+)"
MINUS = r"(?P<MINUS>-)"
MULTIPLY = r"(?P<MULTIPLY>\*)"
DIVIDE = r"(?P<DIVIDE>/)"
MISMATCH = r"(?P<MISMATCH>.+)"

Token = namedtuple("Token", "type value lineno column")

master_pattern = re.compile(
    "|".join(
        [
            FLOAT,
            INTEGER,
            WHITESPACE,
            LPAREN,
            RPAREN,
            VARIABLE,
            PLUS,
            MULTIPLY,
            DIVIDE,
            MINUS,
            ASSIGN,
            MISMATCH,
        ]
    )
)


class Node(abc.ABC):
    @abc.abstractmethod
    def analyze(self, world):
        pass

    @abc.abstractmethod
    def interpret(self, world):
        pass


@dataclass
class Integer(Node):
    token: Token
    value: int | None = None

    def analyze(self, world):
        self.value = int(self.token.value)

    def interpret(self, world):
        return self.value


@dataclass
class Addition(Node):
    left: Node
    right: Node

    def analyze(self, world):
        self.left.analyze(world)
        self.right.analyze(world)

    def interpret(self, world):
        return self.left.interpret(world) + self.right.interpret(world)


def tokens(text, line_index):
    """Generates tokens on demand"""
    for m in master_pattern.finditer(text):
        if m.lastgroup == "MISMATCH":
            raise SyntaxError(
                f"Unrecognized token {m.group()} line {line_index + 1}, column {m.start() + 1}"
            )
        if not m.lastgroup == "WHITESPACE":
            yield Token(m.lastgroup, m.group(), line_index + 1, m.start() + 1)


class Calculator:
    def __init__(self, code):
        self._current_token, self._next_token = None, None
        self._code = code
        self._linecount = 0
        self._tokens = None
        self._world = {}

    def execute(self):
        for line in self._code:
            yield self.eval(line)
            self._linecount += 1

    def eval(self, line):
        """Evaluate program"""
        self._tokens = tokens(line, self._linecount)
        self._current_token, self._next_token = None, None
        self._advance()
        self._tree = self.program()
        import pprint

        pprint.pprint(self._tree)
        self._tree.analyze(self._world)
        return self._tree.interpret(self._world)

    def program(self):
        """program = assignment / expr"""
        self._advance()
        if self._next_token and self._next_token.type == "ASSIGN":
            return self.assignment()
        return self.expr()

    def expr(self):
        """expr = term expr_rhs"""
        left = self.term()
        return self.expr_rhs(left)

    def expr_rhs(self, left):
        """expr_rhs = *(("+" / "-") term)"""
        current_type = self._current_token.type if self._current_token else None
        if current_type not in ["PLUS", "MINUS"]:
            return left

        self._advance()
        right = self.term()
        if current_type == "PLUS":
            op = Addition(left, right)
        else:
            op = Subtraction(left, right)
        return self.expr_rhs(op)

    def term(self):
        """term = unary *(("*" / "/") unary)"""
        term = Integer(self._current_token)
        self._advance()
        return term

    def _advance(self):
        self._current_token, self._next_token = self._next_token, next(
            self._tokens, None
        )

    def _accept(self, token_type):
        if self._next_token.type == token_type:
            self._advance()
            return True

    def _expect(self, token_type):
        if not self._accept(token_type):
            raise SyntaxError(
                f"Expected token {token_type}, found {self._next_token.type}"
            )
