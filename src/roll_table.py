import re
import codecs
import config
from prettytable import PrettyTable
from dice import Dice, Die
from roll_range import RollRange
from roll_table_reference import RollTableReference
from evaluate_numeric import evaluate_numeric

_tables = {}
PART_SEPARATOR = '|'


class MalformedRowError(BaseException):
    pass


def load_table(file):
    if config.DEBUG:
        print('Loading {}'.format(file))
    identifier, table = RollTable.from_file(file)
    _tables[identifier] = table


def get_table(key):
    return _tables[key]


def evaluate_text(self):
    text = self.text
    pattern = r"\[\[@(\w+) ([^\]*]*)(\s?\*(\d+))?\]\]"
    match = re.search(pattern, text)
    roll = None
    mapping = {}

    while match is not None:
        key = match.group(1)
        dice = Dice.from_string(match.group(2))
        multiplier = None
        if match.group(4):
            multiplier = int(match.group(4))
        roll = dice.roll(multiplier=multiplier)
        mapping[key] = roll
        sub = '({})'.format(roll)
        text = re.sub(pattern, sub, text, count=1)
        match = re.search(pattern, text)

    return (text, mapping)


class RollTable():
    def __init__(self, dice, rows, title=None, text=None):
        self.dice = dice
        self.rows = rows
        self.title = title
        self.text = text
        for r in self.rows:
            r.table = self

    def description(self):
        t = PrettyTable([self.dice.description(), self.title])
        for row in self.rows:
            t.add_row([row.range.description(), row.text])
        return t

    def evaluate_text(self):
        return evaluate_text(self) if self.text else None

    def roll(self, modifier=None):
        roll = self.dice.roll(modifier)
        row = self.row(roll)
        (
            row_text,
            row_modifier,
            row_table_references,
            row_value_mapping
        ) = row.evaluate()

        table_text = self.evaluate_text()
        final_text = '{}\n{}'.format(table_text[0], row_text) \
            if table_text is not None \
            else row_text

        return (roll, final_text, row_table_references, row_modifier)

    def row(self, roll):
        return next(r for r in self.rows if r.range.matches(roll))

    @classmethod
    def from_file(cls, file):
        line_number = 1
        rows = []
        text = None
        with codecs.open(file, encoding='utf-8') as f:
            for line in f:
                if line_number == 1:
                    identifier = line.strip()
                elif line_number == 2:
                    parts = line.split(PART_SEPARATOR)
                    dice_part = parts[0]
                    if re.search(r"d\*", dice_part):
                        dice = None
                    else:
                        dice = Dice.from_string(parts[0])
                    title = parts[1].strip()
                    if len(parts) > 2:
                        text = parts[2].strip()
                else:
                    try:
                        rows.append(RollTableRow.from_string(line.strip()))
                    except MalformedRowError:
                        rows.append(RollTableRow.from_string('{}{}{}'.format(
                            line_number - 2,
                            PART_SEPARATOR,
                            line.strip())))
                line_number += 1

        if len(rows) == 0:
            raise Exception('Empty file: {}'.format('file'))

        if dice is None:
            dice = Dice([Die(len(rows))])
        table = cls(dice, rows, title, text)
        return (identifier, table)


class RollTableRow():
    def __init__(self, range, text, table_references=None, modifier=None):
        self.range = range
        self.text = text
        self.table_references = None \
            if (table_references is None or len(table_references) == 0) \
            else table_references
        self.modifier = modifier

    def evaluate(self):
        text, mapping = evaluate_text(self)
        text = ".\n".join(text.split(". "))
        modifier = evaluate_numeric(self.modifier, mapping) \
            if self.modifier is not None else None
        references = [r.with_mapping(mapping) for r in self.table_references] \
            if self.table_references is not None else None
        return (text, modifier, references, mapping)

    @classmethod
    def from_string(cls, string):
        parts = string.split(PART_SEPARATOR)
        if len(parts) < 2:
            raise MalformedRowError

        roll_range = RollRange.from_string(parts[0])
        text = parts[1]

        refs = None
        if len(parts) > 2:
            refs = [
                r for
                r in [
                    RollTableReference.from_string(r) for
                    r in parts[2].split(';')
                ]
                if r is not None
            ]

        mod = None
        if len(parts) > 3 and len(parts[3]) > 0:
            mod = parts[3].replace('–', '-')

        return cls(
            roll_range,
            text,
            refs,
            mod,
        )
