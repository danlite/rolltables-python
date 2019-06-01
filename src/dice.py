import re
from random import randint


def condense_roll():
    return True


def dice_from_string(string):
    d = Dice.from_string(string)

    if d and len(d.dice) == 1 and d.modifier is None:
        return d.dice[0]

    return d


def roll_from_string(string):
    d = dice_from_string(string)

    if d:
        return d.roll()

    return None


class Die():
    def __init__(self, sides, count=1, keep=None):
        if keep and keep > count:
            raise Exception('keep must not be greater than count')
        self.sides = sides
        self.count = count
        self.keep = keep

    @classmethod
    def from_string(cls, string):
        match = re.search(r"(?P<count>\d*)d(?P<sides>\d+)(?:k(?P<keep>\d+))?",
                          string)
        if match:
            sides = int(match.group('sides'))
            count = int(match.group('count')) if match.group('count') else 1
            keep = int(match.group('keep')) if match.group('keep') else None
            return cls(sides, count, keep=keep)
        else:
            return None

    def __str__(self):
        return self.description()

    def description(self):
        keep = 'k{}'.format(self.keep) if self.keep is not None else ''
        return '{}d{}{}'.format(self.count if self.count > 1 else '',
                                self.sides,
                                keep)

    def roll(self, multiplier=None):
        return DieRoll(self, multiplier=multiplier)


class Dice():
    def __init__(self, dice=None, modifier=None):
        if dice is None:
            dice = []
        if modifier and not isinstance(modifier, Modifier):
            raise TypeError
        self.dice = dice
        self.modifier = modifier

    @classmethod
    def from_string(cls, string):
        parts = [Die.from_string(s) or int(s) for s in string.split('+')]
        modifiers = [Modifier(x) for x in parts if type(x) is int]
        dice = [x for x in parts if type(x) is Die]
        modifier = None
        if len(modifiers) > 0:
            modifier = Modifier(0)
            for mod in modifiers:
                modifier += mod

        return cls(dice, modifier)

    def __str__(self):
        return self.description()

    def description(self, include_modifier=True):
        string = ' + '.join([d.description() for d in self.dice])
        if include_modifier and self.modifier is not None:
            string += ' {}'.format(self.modifier.display(space=True))
        return string

    def roll(self, modifier=None, multiplier=None):
        mod = None
        if modifier is not None:
            if not isinstance(modifier, Modifier):
                raise TypeError
            mod = modifier
            mod += self.modifier if self.modifier is not None else Modifier(0)
        elif self.modifier is not None:
            mod = self.modifier
            mod += modifier if modifier is not None else Modifier(0)

        return DiceRoll(self, modifier=mod, multiplier=multiplier)


class Modifier():
    def __init__(self, s):
        if type(s) is str:
            self.value = int(s.replace('–', '-'))
        elif type(s) is int:
            self.value = s
        else:
            raise ValueError()

    def __add__(self, other):
        return Modifier(self.value + other.value)

    def __repr__(self):
        return self.display(space=False)

    def display(self, space=False):
        prefix = '-' if self.value < 0 else '+'
        return '{}{}{}'.format(prefix, ' ' if space else '', abs(self.value))


class Roll():
    def __init__(self):
        self._modifier = None
        self.multiplier = None
        self.numbers = []

    def modifier(self):
        return self._modifier.value if self._modifier is not None else 0

    def modifier_display(self):
        if self._modifier is None:
            return ''

        return ' ' + self._modifier.display(space=True)

    def multiplier_display(self):
        if self.multiplier is not None:
            return ' × {}'.format(self.multiplier)
        return ''

    @property
    def number(self):
        result = self.modifier() + sum(self.numbers)
        multiplier = self.multiplier if self.multiplier is not None else 1
        return result * multiplier


class SingleDieRoll(Roll):
    def __init__(self, sides, modifier=None, multiplier=None):
        self.die = Die(sides)
        self._modifier = modifier
        self.multiplier = multiplier
        number = randint(1, sides)
        self.numbers = [number]

    def __str__(self):
        return '{}{}{} = {}'.format(self.die,
                                    self.modifier_display(),
                                    self.multiplier_display(),
                                    self.numbers[0])

    def to_dict(self):
        d = {
            'dice': str(self.die),
            'result': self.number,
        }
        if self._modifier:
            d['modifier'] = self._modifier.value
        if self.multiplier is not None:
            d['multiplier'] = self.multiplier
        return d


class DieRoll(Roll):
    def __init__(self, die, modifier=None, multiplier=None):
        self.die = die
        self._modifier = modifier
        self.multiplier = multiplier

        rolls = []
        discarded_rolls = []

        for _ in range(die.count):
            rolls.append(SingleDieRoll(die.sides))

        if self.die.keep is not None:
            for _ in range(self.die.count - self.die.keep):
                lowest = min(rolls, key=lambda r: r.number)
                rolls.remove(lowest)
                discarded_rolls.append(lowest)

        self.rolls = rolls
        self.discarded_rolls = discarded_rolls

    @property
    def numbers(self):
        return [r.number for r in self.rolls]

    def __str__(self):
        mod = self.modifier_display()
        mult = self.multiplier_display()
        if len(self.numbers) == 1 or condense_roll():
            return '{}{}{} = {}'.format(self.die, mod, mult, self.number)
        else:
            return '{}{}{} = {}{}{} = {}'.format(
                self.die, mod, mult,
                ' + '.join([str(n) for n in self.numbers]), mod, mult,
                self.number
            )

    def to_dict(self):
        d = {
            'description': str(self),
            'result': self.number,
            'rolls': [r.to_dict() for r in self.rolls],
        }
        if self.discarded_rolls:
            d['discarded_rolls'] = [r.to_dict() for r in self.discarded_rolls]
        if self._modifier:
            d['modifier'] = self._modifier.value
        if self.multiplier is not None:
            d['multiplier'] = self.multiplier
        return d


class DiceRoll(DieRoll):
    def __init__(self, dice, modifier=None, multiplier=None):
        self.dice = dice
        self._modifier = modifier
        self.multiplier = multiplier
        rolls = []
        for die in dice.dice:
            rolls.append(die.roll())
        self.rolls = rolls
        self.discarded_rolls = []

    def __str__(self):
        mod = self.modifier_display()
        mult = self.multiplier_display()
        if len(self.numbers) == 1 or condense_roll():
            return '{}{}{} = {}'.format(
                self.dice.description(include_modifier=False),
                mod,
                mult,
                self.number
            )
        else:
            return '{}{}{} = {}{}{} = {}'.format(
                self.dice.description(include_modifier=False), mod, mult,
                ' + '.join([str(n) for n in self.numbers]), mod, mult,
                self.number
            )


if __name__ == "__main__":
    # print(DiceRoll(Dice.from_string('d100')))

    d = Die.from_string('2d4')
    r = DieRoll(d, Modifier(-2))
    # print(r)

    print(SingleDieRoll(4).to_dict())
    # print(Die.from_string('3d6').roll().to_dict())
    # print(Dice.from_string('3d6 + 3').roll().to_dict())
    # print(Die.from_string('3d6').roll().to_dict())
    # print(Die.from_string('4d6k3').roll().to_dict())
    # print(Dice.from_string('4d6k3+1').roll().to_dict())

    print(roll_from_string('3d6+1').to_dict())
    print(roll_from_string('3d6').to_dict())

    d = Dice.from_string('2d12 + d8')
    # print(DiceRoll(d, Modifier(1)))

    d = Dice.from_string('4d6k3')
    # print(d.roll())
