import pytest

from contracts.bundle import Bundle
from contracts.package import Package


def packages_repo():
    P_db_raw = [[('c.db', 1)], [('c.db', 2)], [('c.db', 3)]]
    P_be_raw = [[('c.db', 1), ('c.rest', 1)], [('c.db', 2), ('c.rest', 1)],
                [('c.db', 1), ('c.rest', 2)]]
    P_ui_raw = [[('c.rest', 1)], [('c.rest', 2)], [('c.rest', 3)]]
    P_ncp_raw = [[], [], []]

    P_db = [Package.create_package(('db', ver, conts)) for (ver, conts) in enumerate(P_db_raw, start=1)]
    P_be = [Package.create_package(('be', ver, conts)) for (ver, conts) in enumerate(P_be_raw, start=1)]
    P_ui = [Package.create_package(('ui', ver, conts)) for (ver, conts) in enumerate(P_ui_raw, start=1)]
    P_ncp = [Package.create_package(('ncp', ver, conts)) for (ver, conts) in enumerate(P_ncp_raw, start=1)]

    packages_repo = P_db + P_be + P_ui + P_ncp

    packages_repo.sort(key=lambda p: str(p), reverse=True)

    return packages_repo

def dependencies_txt():
    return ['db', 'be', 'ui', 'ncp']


class TestBundle:

    def create_bundle(self, trigger_package):
        return Bundle(dependencies_txt(), packages_repo(), trigger_package)

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                'trigger_package': ('db', 4, [('c.db', 1)]),
                'packages': [('db', 4), ('ui', 2), ('be', 3), ('ncp', 3)]
            },
            {
                'trigger_package': ('be', 4, [('c.db', 1), ('c.rest', 1)]),
                'packages': [('db', 1), ('ui', 1), ('be', 4), ('ncp', 3)]
            },
            {
                'trigger_package': None,
                'packages': [('db', 2), ('ui', 1), ('be', 2), ('ncp', 3)]
            },
            {
                'trigger_package': ('ui', 4, [('c.db', 1), ('c.rest', 1)]),
                'packages': [('db', 1), ('ui', 4), ('be', 1), ('ncp', 3)]
            },
        ]
    )
    def test_calculate_success(self, test_case):
        self.do_test_calculate_case(test_case)


    @pytest.mark.parametrize(
        "test_case",
        [
            {
                'trigger_package': ('be', 4, [('c.db', 3), ('c.rest', 4)])
            },
            {
                'trigger_package': ('be', 4, [('c.db', 3), ('c.rest', 4)]),
                'packages': [('db', 1), ('ui', 1), ('be', 4), ('ncp', 3)]
            },

        ]
    )
    def test_calculate_failure(self, test_case):
        with pytest.raises(BaseException) as exc_info:
            self.do_test_calculate_case(test_case)


    def do_test_calculate_case(self, test_case) -> None:
        tp = Package.create_package(test_case['trigger_package']) if test_case['trigger_package'] is not None else None
        bundle = self.create_bundle(tp)

        packages = set(bundle.calculate().values())
        expected_packages = set(Package.create_packages(*test_case['packages']))

        assert packages == expected_packages


def test_calculate():
    assert False


def test_find_next_microservice_package():
    assert False


def test_select_next_microservice_package_out_of_current_contracts():
    assert False


def test_is_package_corresponds_bundle_current_contracts():
    assert False


def test_remove_packages_with_higher_contracts_then():
    assert False


def test_update_bundle_contracts():
    assert False


def test_rest_packages_to_find():
    assert False


def test__package_add():
    assert False
