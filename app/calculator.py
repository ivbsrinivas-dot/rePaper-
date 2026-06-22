from __future__ import annotations

import ast
import operator
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class CalculatorError(ValueError):
    """Raised when a calculator expression cannot be evaluated safely."""


@dataclass(frozen=True)
class Calculation:
    answer: Decimal
    expression: str


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate_percentage(percent_text: str, base_text: str) -> Calculation:
    percent = _to_decimal(percent_text)
    base = _to_decimal(base_text)
    answer = (percent / Decimal("100")) * base
    return Calculation(answer=answer, expression=f"{percent}% of {base}")


def evaluate_expression(expression: str) -> Calculation:
    normalized = _normalize_expression(expression)
    if not normalized:
        raise CalculatorError("Please enter a mathematical expression.")

    try:
        tree = ast.parse(normalized, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError("I could not understand that expression.") from exc

    answer = _eval_node(tree.body)
    return Calculation(answer=answer, expression=normalized)


def format_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f").rstrip("0").rstrip(".")


def _eval_node(node: ast.AST) -> Decimal:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return _to_decimal(str(node.value))

    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Div) and right == 0:
            raise CalculatorError("Division by zero is not allowed.")
        if isinstance(node.op, ast.Pow) and abs(right) > 12:
            raise CalculatorError("That exponent is too large for this simple calculator.")
        return Decimal(str(_OPERATORS[type(node.op)](left, right)))

    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        operand = _eval_node(node.operand)
        return Decimal(str(_OPERATORS[type(node.op)](operand)))

    raise CalculatorError("Only numbers and +, -, *, /, ** operators are supported.")


def _normalize_expression(expression: str) -> str:
    value = expression.lower().strip()
    value = re.sub(r"\bcalculate\b", "", value)
    value = re.sub(r"\bwhat is\b", "", value)
    value = value.replace("x", "*")
    value = value.replace("^", "**")
    return value.strip()


def _to_decimal(value: str) -> Decimal:
    try:
        return Decimal(value.replace(",", "").strip())
    except (InvalidOperation, AttributeError) as exc:
        raise CalculatorError("Please provide valid numbers.") from exc
