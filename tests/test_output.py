import sys
from io import StringIO

from crosspm.helpers.output import LIST, PLAIN, DICT


def test_output_format_shell_one(package, output):
    expected_result = """
PACKAGE_ROOT='/test/path'

"""
    result = output.output_format_shell(packages={'package': package})
    assert expected_result == result


def test_output_format_shell_dependencies(package_root, output):
    assert True
    expected_result = """
PACKAGE2_ROOT='/test/path/package2'
PACKAGE11_ROOT='/test/path/package11'
PACKAGE12_ROOT='/test/path/package12'
PACKAGE1_ROOT='/test/path/package1'

"""
    result = output.output_format_shell(packages=package_root.packages)
    assert expected_result == result


def test_output_format_shell_cmd_one(package, output):
    expected_result = """
set PACKAGE_ROOT=/test/path

"""
    result = output.output_format_cmd(packages={'package': package})
    assert expected_result == result


def test_output_format_cmd_dependencies(package_root, output):
    assert True
    expected_result = """
set PACKAGE2_ROOT=/test/path/package2
set PACKAGE11_ROOT=/test/path/package11
set PACKAGE12_ROOT=/test/path/package12
set PACKAGE1_ROOT=/test/path/package1

"""
    result = output.output_format_cmd(packages=package_root.packages)
    assert expected_result == result


def test_output_format_python_list(package_root, output):
    expected_result = """# -*- coding: utf-8 -*-

PACKAGES_ROOT = ["""
    output._output_config['type'] = LIST
    result = output.output_format_python(packages=package_root.packages)
    assert result.startswith(expected_result)


def test_output_format_python_dict(package_root, output):
    expected_result = """# -*- coding: utf-8 -*-

PACKAGES_ROOT = {"""
    output._output_config['type'] = DICT
    result = output.output_format_python(packages=package_root.packages)
    assert result.startswith(expected_result)


def test_output_format_python_plain(package_root, output):
    expected_result = """# -*- coding: utf-8 -*-

PACKAGE11_ROOT = '/test/path/package11'
PACKAGE12_ROOT = '/test/path/package12'
PACKAGE1_ROOT = '/test/path/package1'
PACKAGE2_ROOT = '/test/path/package2'
"""
    output._output_config['type'] = PLAIN
    result = output.output_format_python(packages=package_root.packages)
    assert result == expected_result


def test_output_format_json(package_root, output):
    expected_result = """{
 "PACKAGES_ROOT": {
  "PACKAGE2_ROOT": "/test/path/package2",
  "PACKAGE11_ROOT": "/test/path/package11",
  "PACKAGE12_ROOT": "/test/path/package12",
  "PACKAGE1_ROOT": "/test/path/package1"
 }
}"""
    result = output.output_format_json(packages=package_root.packages)
    assert result == expected_result


def test_output_format_stdout(package_root, output):
    expected_result = """PACKAGE2_ROOT: /test/path/package2
PACKAGE11_ROOT: /test/path/package11
PACKAGE12_ROOT: /test/path/package12
PACKAGE1_ROOT: /test/path/package1
"""
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    output.output_format_stdout(packages=package_root.packages)

    sys.stdout = old_stdout
    mystdout.seek(0)
    assert expected_result == mystdout.read()


def test_output_jinja2():
    # Создавать темповый файл с
    # for package in packages - {{package.name}}
    #
    # И явно проверять result, какой хотим
    # Удалить темповый файл
    assert True


def test_output_format_lock():
    assert True
