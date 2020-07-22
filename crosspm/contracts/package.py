from datetime import datetime

import dateutil
import time
from addict import Dict

from crosspm.contracts.contracts import Contract
from crosspm.contracts.package_version import PackageVersion


class Package:

    def __init__(self, name: str, version: str, contracts: dict):
        self.name = name
        self.version = PackageVersion(version)
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

    def __lt__(self, other):
        return (self.name, self.version) < (other.name, other.version)

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
    def create_contracts_from_dict(contracts):
        return {k: Contract(k, v) for k, v in contracts.items()}

    @staticmethod
    def create_package(package):

        if len(package) == 3:
            return Package(package[0], str(package[1]), Package.create_contracts(package[2]))

        return Package(package[0], str(package[1]), Package.create_contracts([]))

    @staticmethod
    def create_packages(*packages):
        res = set()
        for p in packages:
            res.add(Package.create_package(p))

        return res

class ArtifactoryPackage(Package):
    def __init__(self, name, version, contracts, art_path, params, params_raw, paths_params, arti_item_find_results):
        super(ArtifactoryPackage, self).__init__(name, version,
                                                 Package.create_contracts_from_dict(contracts))
        self.art_path = art_path
        self.params = params
        self.params_raw = params_raw
        self.paths_params = paths_params
        self.arti_item_find_results = arti_item_find_results

    def strisodate_to_timestamp(self, date):
        return dateutil.parser.parse(date).timestamp()

    def pkg_stat(self):
        stat_pkg = {
            'ctime': self.strisodate_to_timestamp(self.arti_item_find_results.created),
            'mtime': self.strisodate_to_timestamp(self.arti_item_find_results.modified),
            'size': int(self.arti_item_find_results.size)
        }
        return stat_pkg

