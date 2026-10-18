"""Simple python-like parser

ABNF grammar:

root -> funcall / fundef

fundef -> DEF name LPAREN params RPAREN COLON body

funcall -> name LPAREN params RPAREN

params -> expression *( COMMA expression )

expression -> name / integer / addition

addition -> expression PLUS expression

body -> funcall / expression
"""

import abc
from dataclasses import dataclass
from scanner import Token
from pprint import pprint
from typing import Union
from collections import ChainMap


class World:
    def __init__(self, builtins=None):
        if builtins is None:
            builtins = {}
        self.functions = ChainMap({}, builtins)
        self.variables = ChainMap()
        self.call_stack = []

    def __repr__(self):
        return f"functions: {self.functions}, variables: {self.variables}"


class Production(abc.ABC):

    @abc.abstractmethod
    def analyze(self, world: World):
        pass

    @abc.abstractmethod
    def interpret(self, world: World):
        pass


class Expression(Production):
    pass


@dataclass
class Name(Expression):
    token: Token
    value: str | None = None

    def analyze(self, world: World):
        self.value = self.token.matched_text

    def interpret(self, world: World):
        return world.variables[self.value]


@dataclass
class Integer(Expression):
    token: Token
    value: int | None = None

    def analyze(self, world: World):
        self.value = int(self.token.matched_text)

    def interpret(self, world: World):
        return self.value


@dataclass
class Addition(Expression):
    left: Expression
    right: Expression

    def analyze(self, world: World):
        self.left.analyze(world)
        self.right.analyze(world)

    def interpret(self, world: World):
        left_value = self.left.interpret(world)
        right_value = self.right.interpret(world)
        return left_value + right_value


@dataclass
class FunctionDefinition(Production):
    token: Token
    params: list[Expression]
    body: "FunctionBody"

    def analyze(self, world: World):
        """Set lookup table reference to user defined function"""
        world.functions[self.token.matched_text] = self
        for p in self.params:
            p.analyze(world)
        self.body.analyze(world)

    def interpret(self, world: World):
        """Execute body with bound function parameters"""
        evaluated_arguments = world.call_stack[-1]
        local_scope = {
            param.value: argument
            for param, argument in zip(self.params, evaluated_arguments)
        }
        world.variables = world.variables.new_child(local_scope)
        result = self.body.interpret(world)
        world.variables = world.variables.parents
        return result


@dataclass
class FunctionCall(Production):
    token: Token
    arguments: list[Expression]
    function_ref: FunctionDefinition | None = None

    def analyze(self, world: World):
        """Get reference to function from symbol table"""
        funcname = self.token.matched_text
        try:
            self.function_ref = world.functions[funcname]
        except KeyError as exc:
            raise NameError(f"Function {self.token.matched_text} not found") from exc
        for p in self.arguments:
            p.analyze(world)

    def interpret(self, world: World):
        """Call referenced function with provided arguments"""
        arguments = [p.interpret(world) for p in self.arguments]
        if hasattr(self.function_ref, "interpret"):
            # user defined
            world.call_stack.append(arguments)
            result = self.function_ref.interpret(world)
            world.call_stack.pop()
        else:
            # builtin
            result = self.function_ref(*arguments)
        return result


@dataclass
class FunctionBody(Production):
    body: FunctionCall | Expression

    def analyze(self, world: World):
        self.body.analyze(world)

    def interpret(self, world: World):
        return self.body.interpret(world)


class PyParser:

    def __init__(self, scanner):
        self.scanner = scanner
        self.structure = []

    def parse(self):
        while self.scanner.has_tokens():
            self.structure.append(self.root())

    def show(self):
        pprint(self.structure)

    def root(self):
        """root -> funcall / fundef"""

        first = self.scanner.peek()
        if first.name == "DEF":
            return self.function_definition()
        elif first.name == "NAME":
            return self.function_call()
        else:
            raise SyntaxError(f"Unknown root: {first}")

    def match(self, token_types):
        token = self.scanner.match(token_types)
        if token is None:
            expected_types = " or ".join(token_types)
            raise SyntaxError(f"Expected {expected_types}")
        return token

    def function_definition(self):
        """fundef -> DEF name LPAREN params RPAREN COLON body"""

        self.match(["DEF"])
        name = self.match(["NAME"])
        self.match(["LPAREN"])
        params = self.parameters()
        self.match(["RPAREN"])
        self.match(["COLON"])
        body = self.body()
        return FunctionDefinition(name, params, body)

    def function_call(self):
        """funcall -> name LPAREN params RPAREN"""

        name = self.match(["NAME"])
        self.match(["LPAREN"])
        params = self.parameters()
        self.match(["RPAREN"])
        return FunctionCall(name, params)

    def parameters(self):
        """Params -> expression *( COMMA expression )"""

        params = []
        nxt = self.scanner.peek()
        while nxt.name != "RPAREN":
            param = self.expression()
            params.append(param)
            nxt = self.scanner.peek()
            if nxt.name != "RPAREN":
                self.match(["COMMA"])
        return params

    def expression(self):
        """expression -> name / integer / addition"""

        nxt = self.scanner.peek()
        match nxt.name:
            case "NAME":
                name = Name(self.match(["NAME"]))
                nxt = self.scanner.peek()
                if nxt.name == "PLUS":
                    return self.addition(name)
                else:
                    return name

            case "INTEGER":
                integer = Integer(self.match(["INTEGER"]))
                nxt = self.scanner.peek()
                if nxt.name == "PLUS":
                    return self.addition(integer)
                else:
                    return integer

    def addition(self, left):
        """addition -> expression PLUS expression"""

        self.match(["PLUS"])
        right = self.expression()
        return Addition(left, right)

    def body(self):
        """body -> funcall / expression"""

        head, following = self.match(["INTEGER", "NAME"]), self.scanner.peek()
        # If integer: options are integer/addition
        if head.name == "INTEGER":
            if following and following.name == "PLUS":
                # body is calculated expression
                self.scanner.push(head)
                body = self.expression()
            else:
                # body is a single integer expression
                body = Integer(head)
        elif head.name == "NAME":
            if following and following.name == "PLUS":
                # body is calculated expression
                self.scanner.push(head)
                body = self.expression()
            elif following and following.name == "LPAREN":
                # body is funcall
                self.scanner.push(head)
                body = self.function_call()
            else:
                # body is named expression
                body = Name(head)
        else:
            # unrecogized body
            raise SyntaxError(
                f"Expected function body, got sequence: {head.name}, {following.name}"
            )
        return FunctionBody(body)
