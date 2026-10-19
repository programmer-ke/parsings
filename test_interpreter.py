from scanner import Scanner, TOKEN_SPEC
from parser import PyParser, World
from analyzer import Analyzer
from interpreter import Interpreter
from pprint import pprint
import pytest


def test_simple_addition():
    scanner = Scanner(TOKEN_SPEC)
    code = [
        "print(1 + 2)",
    ]
    scanner.scan(code)
    parser = PyParser(scanner)
    parser.parse()

    parser.show()

    # prepare builtins
    builtins = {"print": print}
    symbol_table = World(builtins)
    analyzer = Analyzer(symbol_table, parser.structure)
    analyzer.analyze()
    interpreter = Interpreter(symbol_table, parser.structure)
    result = interpreter.interpret()
    print("interpreter result", result)


def test_nested_addition():
    scanner = Scanner(TOKEN_SPEC)
    code = [
        "print(1 + 2 + 3)",
    ]
    scanner.scan(code)
    parser = PyParser(scanner)
    parser.parse()

    parser.show()

    # prepare builtins
    builtins = {"print": print}
    symbol_table = World(builtins)
    analyzer = Analyzer(symbol_table, parser.structure)
    analyzer.analyze()
    interpreter = Interpreter(symbol_table, parser.structure)
    result = interpreter.interpret()
    print("interpreter result", result)


def test_user_function_call():
    scanner = Scanner(TOKEN_SPEC)
    code = [
        "def print_sum(x, y):",
        "    print(x + y)",
        "print_sum(10, 20)",
    ]
    scanner.scan(code)
    parser = PyParser(scanner)
    parser.parse()

    parser.show()

    # prepare builtins
    builtins = {"print": print}
    symbol_table = World(builtins)
    analyzer = Analyzer(symbol_table, parser.structure)
    analyzer.analyze()
    interpreter = Interpreter(symbol_table, parser.structure)
    result = interpreter.interpret()
    print("interpreter result", result)


def test_user_function_call_with_result():
    scanner = Scanner(TOKEN_SPEC)
    code = [
        "def sum(x, y):",
        "    x + y",
        "sum(123, 456)",
    ]
    scanner.scan(code)
    parser = PyParser(scanner)
    parser.parse()

    parser.show()

    # prepare builtins
    builtins = {"print": print}
    symbol_table = World(builtins)
    analyzer = Analyzer(symbol_table, parser.structure)
    analyzer.analyze()
    interpreter = Interpreter(symbol_table, parser.structure)
    result = interpreter.interpret()
    print("interpreter result", result)


def test_scope_handling():
    scanner = Scanner(TOKEN_SPEC)
    code = [
        "def g(y):",
        "    x + y",
        "def f(x):",
        "    g(1)" "f(5)",
    ]
    scanner.scan(code)
    parser = PyParser(scanner)
    parser.parse()

    parser.show()

    # prepare builtins
    builtins = {"print": print}
    symbol_table = World(builtins)
    analyzer = Analyzer(symbol_table, parser.structure)
    analyzer.analyze()
    interpreter = Interpreter(symbol_table, parser.structure)
    with pytest.raises(NameError):
        result = interpreter.interpret()
