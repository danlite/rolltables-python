import re
from dice import Dice, Roll


def evaluate_numeric(expression, mapping=None):
    if isinstance(expression, Roll):
        return expression.number

    if isinstance(expression, int):
        return expression

    match = re.search(r"\[\[(.*)(\s?\*(\d+))?\]\]", expression)
    if match:
        multiplier = None
        if match.group(3):
            multiplier = int(match.group(3))
        return Dice.from_string(match.group(1)).roll(multiplier).number

    if mapping and type(expression) is str:
        match = re.search(r"@(\w+)", expression)
        if match:
            return evaluate_numeric(mapping[match.group(1)])

    return int(expression)
