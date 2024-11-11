from collections import OrderedDict

import pytest

from crosspm.helpers.output import Output
from crosspm.helpers.package import Package


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "artifactoryaql: testing artifactoryaql"
    )


@pytest.fixture(scope="function")
def package():
    params = {'arch': 'x86', 'osname': 'win', 'package': 'package'}
    params_found = {'repo': 'lib-cpp-release', 'version': '1.2.3'}
    _package = Package('package', None, params, None, None, None, params_found, None, None)
    _package.unpacked_path = "/test/path"
    yield _package


@pytest.fixture(scope="function")
def package_root():
    """
    Create root with dependencies:
    root
    - package1
      - package11
      - package12
    - package2
    """
    params = {'arch': 'x86', 'osname': 'win', 'package': 'root'}
    _root = Package('root', None, params, None, None, None, None, None, None)

    params = {'arch': 'x86', 'osname': 'win', 'package': 'package1'}
    _package1 = Package('package1', None, params, None, None, None, None, None, None)

    params = {'arch': 'x86', 'osname': 'win', 'package': 'package11'}
    _package11 = Package('package11', None, params, None, None, None, None, None, None)

    params = {'arch': 'x86', 'osname': 'win', 'package': 'package12'}
    _package12 = Package('package12', None, params, None, None, None, None, None, None)

    params = {'arch': 'x86', 'osname': 'win', 'package': 'package2'}
    _package2 = Package('package2', None, params, None, None, None, None, None, None)

    _package1.packages = OrderedDict([('package11', _package11), ('package12', _package12)])
    _root.packages = OrderedDict([('package2', _package2), ('package1', _package1)])
    for _package in _root.all_packages:
        _package.unpacked_path = "/test/path/{}".format(_package.name)
    yield _root


@pytest.fixture
def output():
    _output = Output(data=None, name_column='package', config=None)
    yield _output
