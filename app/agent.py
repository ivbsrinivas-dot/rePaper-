from __future__ import annotations

import re
from dataclasses import dataclass

from app.calculator import (
    Calculation,
    CalculatorError,
    calculate_percentage,
    evaluate_expression,
    format_decimal,
)


@dataclass(frozen=True)
class AgentResponse:
    input: str
    task: str
    tool: str
    answer: str
    expression: str


_PERCENT_PATTERN = re.compile(
    r"(?P<percent>-?\d+(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?)\s*%\s*(?:of|from)?\s*"
    r"(?P<base>-?\d+(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def run_calculator_agent(user_input: str) -> AgentResponse:
    clean_input = user_input.strip()
    if not clean_input:
        raise CalculatorError("Please enter a math question.")

    calculation = _calculate(clean_input)
    task = _describe_task(clean_input)

    return AgentResponse(
        input=clean_input,
        task=task,
        tool="calculator",
        answer=format_decimal(calculation.answer),
        expression=calculation.expression,
    )


def _calculate(user_input: str) -> Calculation:
    percent_match = _PERCENT_PATTERN.search(user_input)
    if percent_match:
        return calculate_percentage(percent_match.group("percent"), percent_match.group("base"))

    return evaluate_expression(user_input)


def _describe_task(user_input: str) -> str:
    if _PERCENT_PATTERN.search(user_input):
        return "I need percentage calculation"
    return "I need arithmetic calculation"
