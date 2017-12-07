# -*- coding: utf-8 -*-
import os


def test_package_tree(package_root):
    packages = [x.name for x in package_root.all_packages]
    assert packages == ['package11', 'package12', 'package2', 'package1']


def test_public_interface(package):
    """
    Test public interface, which documented in docs/USAGE-PYTHON.md and people can use this attribute in python-code
    """
    assert hasattr(package, 'name')
    assert hasattr(package, 'packed_path')
    assert hasattr(package, 'unpacked_path')
    assert hasattr(package, 'duplicated')

    assert hasattr(package, 'packages')
    assert isinstance(package.packages, dict)

    # Legacy get_name_and_path
    assert package.get_name_and_path() == (package.name, package.unpacked_path)

    assert os.path.normpath(package.get_file_path('some.exe')) == os.path.normpath('/test/path/some.exe')
    assert package.get_file('not-exist.exe', unpack_force=False) is None

    assert isinstance(package.get_params(), dict)
    assert package.get_params()['osname'] == 'win'
