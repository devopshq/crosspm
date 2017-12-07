from crosspm.helpers.output import Output
import pytest
import os


@pytest.fixture
def output():
    _output = Output(data=None, name_column='package', config=None)
    yield _output


def test_output_type_stdout():
    assert True


def test_output_type_lock():
    assert True


def test_output_type_shell_one(package, output):
    expected_result = """
PACKAGE_ROOT='/test/path'

"""
    result = output.output_type_shell(packages={'package': package})
    assert expected_result == result


def test_output_type_shell_dependencies(package_root, output):
    assert True
    expected_result = """
PACKAGE2_ROOT='/test/path/package2'
PACKAGE11_ROOT='/test/path/package11'
PACKAGE12_ROOT='/test/path/package12'
PACKAGE1_ROOT='/test/path/package1'

"""
    result = output.output_type_shell(packages=package_root.packages)
    assert expected_result == result
