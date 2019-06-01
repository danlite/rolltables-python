import re


class RollRange():
    def __init__(self, min, max):
        self.min = min
        self.max = max

    @classmethod
    def from_string(cls, string):
        s = string.replace(' ', '')
        match = re.search(r"(\d*)[^\d](\d*)", s)
        if match:
            min = int(match.group(1)) if len(match.group(1)) > 0 else None
            max = int(match.group(2)) if len(match.group(2)) > 0 else None
            return cls(min, max)
        else:
            if re.search(r"^\d+$", s):
                return cls(int(s), int(s))
            return cls(None, None)

    def description(self):
        if self.min is not None and self.max is not None:
            if self.min == self.max:
                return '{}'.format(self.min)
            else:
                return '{}-{}'.format(self.min, self.max)
        elif self.min is not None:
            return '{} or greater'.format(self.min)
        elif self.max is not None:
            return '{} or less'.format(self.max)
        else:
            return 'Any'

    def matches(self, roll):
        n = roll.number
        if self.min is not None and self.max is not None:
            return n <= self.max and n >= self.min
        elif self.min is not None:
            return n >= self.min
        elif self.max is not None:
            return n <= self.max
        else:
            return True
