import pytest

from app.agent import run_calculator_agent
from app.calculator import CalculatorError


def test_percentage_calculation():
    response = run_calculator_agent("calculate 20% of 8500")

    assert response.task == "I need percentage calculation"
    assert response.answer == "1700"
    assert response.tool == "calculator"


def test_arithmetic_calculation():
    response = run_calculator_agent("calculate 10 + 5 * 2")

    assert response.task == "I need arithmetic calculation"
    assert response.answer == "20"


def test_rejects_unknown_expression():
    with pytest.raises(CalculatorError):
        run_calculator_agent("calculate square root of 9")
