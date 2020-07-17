import pytest

from contracts.contracts import Contract


class TestContract():
    def test_equality(self):
        assert Contract('c.db', '12') == Contract('c.db', '12')
        assert Contract('c.db', '12') != Contract('c.db', '15')
        assert Contract('c.db', '12') != Contract('c.rest', '12')

    # def test_contracts_intersection(self):
    #     assert {Contract('c.db', '1')} == PackageContracts.create({'c.rest': '1', 'c.db': '2'})
