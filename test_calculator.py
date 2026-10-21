from calc import Calculator


def test_returns_value_last_expression_statement():
    code = ["123", "456"]
    assert list(Calculator(code).execute()) == [123, 456]
