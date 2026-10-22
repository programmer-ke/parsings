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


def test_assignment():
    code = ["a = 2", "a", "b = a + 3", "b"]
    expected = [None, 2, None, 5]
    assert list(Calculator(code).execute()) == expected


explicit_pairs = (
    (["x = 1", "x"], [None, 1]),
    (["long_var_name2 = 5", "long_var_name2"], [None, 5]),
    (["x = 1", "x = 2", "x"], [None, None, 2]),
    (["x = 1", "y = x", "x = 2", "y"], [None, None, None, 1]),
    (["x = 2", "y = x * 3", "y"], [None, None, 6]),
    (["x = 2", "x + x"], [None, 4]),
    (["x = 2", "x = x + 1", "x"], [None, None, 3]),
    (["x = 3", "(x + 1) * 2"], [None, 8]),
    (["x = -2", "y = x * -3", "y"], [None, None, 6]),
    (["x = 2", "x = 3"], [None, None]),
)


@pytest.mark.parametrize("code, expected", explicit_pairs)
def test_variable_values(code, expected):
    assert list(Calculator(code).execute()) == expected


variable_errors = (
    "x == 2",
    "x = 2 = 3",
    "2x = 1",
    "_x = 1",
)


@pytest.mark.parametrize("expr", variable_errors)
def test_variable_syntax_errors(expr):
    with pytest.raises(SyntaxError):
        list(Calculator([expr]).execute())


def test_undefined_variable():
    with pytest.raises(KeyError):
        list(Calculator(["x + 1"]).execute())


def test_undefined_variable_in_assignment():
    with pytest.raises(KeyError):
        list(Calculator(["y = x"]).execute())
