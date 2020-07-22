import pytest

from package_parsers.debian_package_name_parser import DebianPackageNameParser


class TestTadPackage:

    @pytest.mark.parametrize(
        "test_case",
        [
            ['tad-db-schema_2.5.9.314_all.deb', 'tad-db-schema', '2.5.9.314', 'all'],
            ['tad-backend_2.5.317_all.deb', 'tad-backend', '2.5.317', 'all'],
        ]
    )
    def test_parse_from_package_name(self, test_case):
        p = DebianPackageNameParser.parse_from_package_name(test_case[0])
        assert p.package == test_case[1]
        assert p.version == test_case[2]
        assert p.arch == test_case[3]
        assert p.fullname == test_case[0]
