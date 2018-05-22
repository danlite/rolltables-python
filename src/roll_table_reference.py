import re
from json import loads
from evaluate_numeric import evaluate_numeric


class RollTableReference(object):
    def __init__(self, identifier, count=1, opts={}):
        self.identifier = identifier
        self.count = count
        self.opts = opts

    @classmethod
    def from_string(cls, string):
        if string:
            parts = string.split('.')
            identifier = parts[0]
            count = 1
            opts = {}

            if len(parts) > 1:
                match = re.search(r"(\d+)?(\{.*\})?", parts[1])
                if match and match.group(1):
                    count = match.group(1)
                if match and match.group(2):
                    opts = loads(match.group(2))

            return cls(identifier, count, opts)
        else:
            return None

    def with_mapping(self, mapping):
        return RollTableReference(self.identifier,
                                  evaluate_numeric(self.count, mapping),
                                  self.opts)

    # def roll(self, modifier=None):
    #     table = get_table(self.identifier)
    #     if table:
    #         rolls = []
    #         for _ in range(self.count):
    #             rolls.append(table.roll(modifier))
    #     else:
    #         None
