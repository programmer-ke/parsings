from calc import Calculator


def test_returns_primitive_value():
    code = ["123", "456"]
    assert list(Calculator(code).execute()) == [123, 456]


def test_can_calculate():
    expr = "123 + 456 + 789"
    [result] = Calculator([expr]).execute()
    assert result == 123 + 456 + 789
