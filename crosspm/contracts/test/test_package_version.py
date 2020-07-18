from contracts.package_version import PackageVersion

class TestPackageVersion:


    def test_package_version():
        assert PackageVersion("1.2.3") < PackageVersion("10.2.3")
        assert PackageVersion("1.3") < PackageVersion("1.3.1")
        assert PackageVersion("1.2.3") < PackageVersion("1.2.3-feature1-super-puper")

        assert PackageVersion("1.2.3") != PackageVersion("1.2.3-feature1-super-puper")
        assert PackageVersion("1.3") == PackageVersion("1.3.0")


    def test_package_version_properties():
        package_version = PackageVersion("1.2.3-feature1-super-puper")

        assert 1 == package_version.major
        assert 2 == package_version.minor
        assert 3 == package_version.micro
        assert 'feature1.super.puper' == package_version.local

