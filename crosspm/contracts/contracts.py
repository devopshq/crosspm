class Contract:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __hash__(self):
        return hash((self.name, self.value))

    def __str__(self):
        return "{}.{}".format(self.name, self.value)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __ne__(self, other):
        return not (self == other)

class PackageContracts:
    def __init__(self, contracts):
        self._contracts = contracts

    def __getitem__(self, key):
        for c in self._contracts:
            if c.name == key.name:
                return c

        return None

    def is_lower(self, contract):
        c = self[contract]
        return c and c.value < contract.value


