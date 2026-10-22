import pytest
from calc import Calculator


pairs = (
    ("123", 123),
    ("456", 456),
    ("123 + 456 + 789", 123 + 456 + 789),
    ("-1", -1),
    ("2 / -2", 2 / -2),
    ("(1 + 2) * 3", (1 + 2) * 3),
)


@pytest.mark.parametrize("program, expected", pairs)
def test_can_calculate(program, expected):
    expr = "123 + 456 + 789"
    [result] = Calculator([program]).execute()
    assert result == expected
