import pytest

from apier.templates.python_tree.base.internal.expressions.evaluation import eval_expr


@pytest.mark.parametrize(
    "expression, variables, expected",
    [
        ("1 + 2 - 3", None, 0),
        ("1+2-3", None, 0),
        ("len([1, 2, 3])", None, 3),
        ("len((1, 2)) + 5", None, 7),
        ("len('hello')", None, 5),
        ("'hello' + ' world'", None, "hello world"),
        ("3.14159", None, 3.14159),
        ("3 == 3", None, True),
        ("3 != 3", None, False),
        ("4 < 5", None, True),
        ("4 > 5", None, False),
        ("4 <= 4", None, True),
        ("4 >= 4", None, True),
        ("len([1]) >= 2", None, False),
        ("3 + (-1)", None, 2),
        ("3 +(1+(2 * ((3 + 4-1)-  5)  ))", None, 6),
        ("3 * (2 + 1)", None, 9),
        ("3 / (2 + 1)", None, 1.0),
        ("round(3.14159)", None, 3),
        ("floor(5)", None, 5),
        ("ceil(5)", None, 5),
        ("floor(5.9)", None, 5),
        ("ceil(5.9)", None, 6),
        ("floor(-5.9)", None, -6),
        ("ceil(-5.9)", None, -5),
        ("x + y", {"x": 1, "y": 2}, 3),
        ("a * b + c", {"a": 2, "b": 3, "c": 1}, 7),
        ("1 + len([x, y])", {"x": 1, "y": 2}, 3),
        ("(a + b) * c", {"a": 1, "b": 2, "c": 3}, 9),
    ],
)
def test_eval_expr(expression, variables, expected):
    result = eval_expr(expression, variables)
    assert result == expected


@pytest.mark.parametrize(
    ("expression", "error"),
    [
        ("5j", ValueError("Complex numbers are not supported.")),
        ("x + y", ValueError("Variable not defined: x")),
        ("x ** 2", SyntaxError("Unsupported syntax: BinOp")),
        ("x + ", SyntaxError("invalid syntax")),
        ("1 + foo()", ValueError("Function not allowed: 'foo'")),
        ("1 < 2 < 3", ValueError("Only simple comparisons are supported.")),
        ("1 in [1, 2, 3]", ValueError("Comparison operator not allowed: In")),
    ],
)
def test_eval_expr_errors(expression, error):
    with pytest.raises(type(error)) as exc_info:
        eval_expr(expression)
    assert str(error) in str(exc_info.value)
