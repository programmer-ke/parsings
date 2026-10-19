from scanner import Scanner, TOKEN_SPEC
from parser import PyParser, World
from analyzer import Analyzer
from pprint import pprint
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
    parser.parse()

    # prepare builtins
    builtins = {"print": print}
    symbol_table = World(builtins)
    analyzer = Analyzer(symbol_table, parser.structure)
    analyzer.analyze()

    pprint(symbol_table)


def test_argument_count_mismatch_caught():
    scanner = Scanner(TOKEN_SPEC)
    code = [
        "def print_sum(x, y):",
        "    print(x + y)",
        "print_sum(10, 20, 3)",
    ]
    scanner.scan(code)
    parser = PyParser(scanner)
    parser.parse()

    # prepare builtins
    builtins = {"print": print}
    symbol_table = World(builtins)
    analyzer = Analyzer(symbol_table, parser.structure)
    with pytest.raises(TypeError):
        analyzer.analyze()
