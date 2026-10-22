import re
import abc
import pprint
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
class Float(Node):
    token: Token
    value: float | None = None

    def analyze(self, world):
        self.value = float(self.token.value)

    def interpret(self, world):
        return self.value


@dataclass
class Variable(Node):
    token: Token
    name: str | None = None

    def analyze(self, world):
        self.name = str(self.token.value)

    def interpret(self, world):
        return world[self.name]


@dataclass
class Addition(Node):
    left: Node
    right: Node

    def analyze(self, world):
        self.left.analyze(world)
        self.right.analyze(world)

    def interpret(self, world):
        return self.left.interpret(world) + self.right.interpret(world)


@dataclass
class Multiplication(Node):
    left: Node
    right: Node

    def analyze(self, world):
        self.left.analyze(world)
        self.right.analyze(world)

    def interpret(self, world):
        return self.left.interpret(world) * self.right.interpret(world)


@dataclass
class Subtraction(Node):
    left: Node
    right: Node

    def analyze(self, world):
        self.left.analyze(world)
        self.right.analyze(world)

    def interpret(self, world):
        return self.left.interpret(world) - self.right.interpret(world)


@dataclass
class Division(Node):
    left: Node
    right: Node

    def analyze(self, world):
        self.left.analyze(world)
        self.right.analyze(world)

    def interpret(self, world):
        return self.left.interpret(world) / self.right.interpret(world)


@dataclass
class Positive(Node):
    factor: Node

    def analyze(self, world):
        self.factor.analyze(world)

    def interpret(self, world):
        return self.factor.interpret(world)


@dataclass
class Negative(Node):
    factor: Node

    def analyze(self, world):
        self.factor.analyze(world)

    def interpret(self, world):
        return -1 * self.factor.interpret(world)


@dataclass
class Assignment(Node):
    variable: Node
    expr: Node

    def analyze(self, world):
        self.variable.analyze(world)
        self.expr.analyze(world)

    def interpret(self, world):
        name, value = self.variable.name, self.expr.interpret(world)
        world[name] = value


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
        self._current_token, self._next_token, self._third_token = None, None, None
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
        self._reset_token_queue()
        self._tree = self.program()
        self._tree.analyze(self._world)
        return self._tree.interpret(self._world)

    def show_tree(self):
        pprint.pprint(self._tree)

    def program(self):
        """program = assignment / expr"""
        if self._third_token and self._third_token.type == "ASSIGN":
            return self.assignment()
        return self.expr()

    def assignment(self):
        """assignment = variable "=" expr"""

        self._expect("VARIABLE")
        variable = Variable(self._current_token)
        self._expect("ASSIGN")
        expr = self.expr()
        return Assignment(variable, expr)

    def expr(self):
        """expr = term expr_rhs"""
        left = self.term()
        return self.expr_rhs(left)

    def expr_rhs(self, left):
        """expr_rhs = *(("+" / "-") term)"""

        op = None
        if self._accept("PLUS"):
            right = self.term()
            op = Addition(left, right)
        elif self._accept("MINUS"):
            right = self.term()
            op = Subtraction(left, right)

        if op is None:
            return left
        return self.expr_rhs(op)

    def term(self):
        """term = unary term_rhs"""
        left = self.unary()
        return self.term_rhs(left)

    def term_rhs(self, left):
        """term_rhs = *(("*" / "/") unary)"""

        op = None
        if self._accept("MULTIPLY"):
            right = self.unary()
            op = Multiplication(left, right)
        elif self._accept("DIVIDE"):
            right = self.unary()
            op = Division(left, right)

        if op is None:
            return left
        return self.term_rhs(op)

    def unary(self):
        """unary = ([ "-" / "+" ] unary) / factor"""

        if self._accept("PLUS"):
            result = Positive(self.unary())

        elif self._accept("MINUS"):
            result = Negative(self.unary())

        else:
            result = self.factor()
        return result

    def factor(self):
        """factor = float / integer / variable / "(" expr ")"""

        if self._accept("FLOAT"):
            return Float(self._current_token)
        elif self._accept("INTEGER"):
            return Integer(self._current_token)
        elif self._accept("VARIABLE"):
            return Variable(self._current_token)
        else:
            self._expect("LPAREN")
            expr = self.expr()
            self._expect("RPAREN")
            return expr

    def _reset_token_queue(self):
        """Start token consumption from new stream"""
        self._current_token, self._next_token, self._third_token = None, None, None
        # First token should be in _next_token slot
        self._advance()
        self._advance()

    def _advance(self):
        self._current_token, self._next_token, self._third_token = (
            self._next_token,
            self._third_token,
            next(self._tokens, None),
        )

    def _accept(self, token_type):
        if self._next_token and self._next_token.type == token_type:
            self._advance()
            return True

    def _expect(self, token_type):
        if not self._accept(token_type):
            raise SyntaxError(f"Expected token {token_type}, found {self._next_token}")
