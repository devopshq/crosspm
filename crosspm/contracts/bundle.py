from ordered_set import OrderedSet
from operator import itemgetter, attrgetter

class Bundle:
    def __init__(self, deps, packages_repo, trigger_package):
        # it is vital for deps to be list, orderedset (or something with insertion order savings),
        # we need the order of packages in dependencies.txt to take next package
        # when no contracts satisfied
        self._deps = OrderedSet(deps)
        self._packages_repo = sorted(packages_repo, reverse=True)
        self._trigger_package = trigger_package

        self._packages = dict()
        self._bundle_contracts = {}

    def calculate(self):

        if self._trigger_package:
            self._packages[self._trigger_package.name] = self._trigger_package

        while True:
            rest_packages_to_find = self.rest_packages_to_find(self._deps, self._packages)
            if not rest_packages_to_find:
                break

            self.update_bundle_contracts()
            self.find_next_microservice_package(rest_packages_to_find)

        return self._packages

    def find_next_microservice_package(self, rest_packages_to_find):
        next_packages_out_of_current_contracts = dict()
        package_lowering_contract = []

        for m in rest_packages_to_find:
            for p in [i for i in self._packages_repo if i.is_microservice(m)]:
                package = self.is_package_corresponds_bundle_current_contracts(next_packages_out_of_current_contracts, p,
                                                                               self._bundle_contracts, package_lowering_contract)
                if package:
                    self._package_add(package)
                    return

            if package_lowering_contract:
                p = package_lowering_contract[0]

                self.remove_packages_with_higher_contracts_then(p)
                self._package_add(p)

                return

        package = self.select_next_microservice_package_out_of_current_contracts(next_packages_out_of_current_contracts, rest_packages_to_find)
        if package:
            self._package_add(package)
            return

        raise BaseException("cant select next package for current contracts:\n"
                            "next_packages_out_of_current_contracts : {}\n"
                            "rest_packages_to_find : {}"
                            .format(next_packages_out_of_current_contracts, rest_packages_to_find))

    def select_next_microservice_package_out_of_current_contracts(self, next_packages_out_of_current_contracts, select_order):
        for i in select_order:
            if i in next_packages_out_of_current_contracts:
                return next_packages_out_of_current_contracts[i]

        return None

    def is_package_corresponds_bundle_current_contracts(self, next_packages_out_of_current_contracts, package,
                                                        bundle_contracts, package_lowering_contract):

        intersection_package_contracts = package.calc_contracts_intersection(bundle_contracts)

        if not intersection_package_contracts:
            cp = None
            if package.name in next_packages_out_of_current_contracts:
                cp = next_packages_out_of_current_contracts[package.name]

            if cp is None:
                next_packages_out_of_current_contracts[package.name] = package
            elif cp.version < package.version:
                next_packages_out_of_current_contracts[package.name] = package

            return None

        failed_contracts = set(intersection_package_contracts)
        for c in intersection_package_contracts:

            if package.contracts[c] == bundle_contracts[c]:
                failed_contracts.discard(c)

            if package.contracts[c].value < bundle_contracts[c].value:
                if not package_lowering_contract:
                    package_lowering_contract.append(package)
                elif package_lowering_contract[0].is_contract_lower_then(package.contracts[c]):
                    package_lowering_contract.clear();
                    package_lowering_contract.append(package)


        if not failed_contracts:
            return package

    def remove_packages_with_higher_contracts_then(self, package_lowering_contract):

        for p in [*self._packages.values()]:
            if p.is_any_contract_higher(package_lowering_contract):
                if self._trigger_package is not None and self._trigger_package == p:
                    raise BaseException(
                        "no tree resolve with trigger_package {} has no appropriate packages with specified package contracts"
                        .format(self._trigger_package))
                del self._packages[p.name]

    def update_bundle_contracts(self):
        self._bundle_contracts = dict()
        for p in self._packages.values():
            self._bundle_contracts.update(p.contracts)

    def rest_packages_to_find(self, deps, packages):
        return deps - packages.keys()

    def _package_add(self, package):
        self._packages[package.name] = package
