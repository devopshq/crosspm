from crosspm.contracts.contracts import Contract


class Package:

    def __init__(self, name, version, contracts):
        self.name = name
        self.version = int(version)
        self.contracts = contracts

    def __hash__(self):
        return hash(str(self.name) + str(self.version))

    def __str__(self):
        return "{}.{}({})".format(self.name, self.version, ",".join(str(s) for s in self.contracts.values()))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version

    def __ne__(self, other):
        return not (self == other)

    def is_microservice(self, microservice):
        return self.name == microservice

    def is_contract_lower_then(self, other):
        if other.name in self.contracts:
            return self.contracts[other.name].value < other.value

        raise BaseException("package {} has no contract {}", str(self), str(other))

    def is_contract_higher_then(self, other):
        if other.name in self.contracts:
            return self.contracts[other.name].value > other.value

        raise BaseException("package {} has no contract {}", str(self), str(other))

    def is_any_contract_higher(self, other):
        for c in self.calc_contracts_intersection(other.contracts):
            if self.contracts[c].value > other.contracts[c].value:
                return True

        return False

    def calc_contracts_intersection(self, contracts):
        return self.contracts.keys() & contracts.keys()

    @staticmethod
    def create_contracts(contracts):
        return {c[0]: Contract(c[0], c[1]) for c in contracts}

    @staticmethod
    def create_package(package):

        if len(package) == 3:
            return Package(package[0], package[1], Package.create_contracts(package[2]))

        return Package(package[0], package[1], Package.create_contracts([]))

    @staticmethod
    def create_packages(*packages):
        res = set()
        for p in packages:
            res.add(Package.create_package(p))

        return res
