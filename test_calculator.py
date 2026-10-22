import pytest
from calc import Calculator

pairs = (
    # basic
    ("123", 123),
    ("456", 456),
    ("123 + 456 + 789", 123 + 456 + 789),
    ("-1", -1),
    ("2 / -2", 2 / -2),
    ("(1 + 2) * 3", (1 + 2) * 3),
    # precedence
    ("2 + 3 * 4", 14),
    ("2 * 3 + 4", 10),
    ("12 / 3 / 2", 2),
    ("12 - 3 - 2", 7),
    # unary
    ("+5", 5),
    ("3 * -2", -6),
    ("3--2", 5),
    ("--3", 3),
    # floats
    ("1.5 + 2.5", 4.0),
    (".5", 0.5),
    ("5.", 5.0),
    ("2.0 * 3", 6.0),
    # nested parens
    ("((2))", 2),
    ("-(2 + 3)", -5),
    ("(1 + 2) * (3 + 4)", 21),
    # int/float mix
    ("1 + 2.5", 3.5),
    ("5 / 2", 2.5),
)


@pytest.mark.parametrize("expr, expected", pairs)
def test_calculate(expr, expected):
    [result] = Calculator([expr]).execute()
    assert result == expected


error_cases = (
    "1 +",
    "(1 + 2",
    "1 $ 2",
)


@pytest.mark.parametrize("expr", error_cases)
def test_syntax_errors(expr):
    with pytest.raises(SyntaxError):
        list(Calculator([expr]).execute())
