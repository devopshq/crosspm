# -*- coding: utf-8 -*-
import os
from collections import OrderedDict
from unittest import TestCase

import pytest

from crosspm.helpers.package import Package


class TestPackage(TestCase):
    _package = Package('package', None, None, None, None, None, None, None, None)
    _package.unpacked_path = "/test/path"

    _root = Package('root', None, None, None, None, None, None, None, None)
    _package1 = Package('package1', None, None, None, None, None, None, None, None)
    _package11 = Package('package11', None, None, None, None, None, None, None, None)
    _package12 = Package('package12', None, None, None, None, None, None, None, None)
    _package1.packages = OrderedDict([('package11', _package11), ('package12', _package12)])

    _package2 = Package('package2', None, None, None, None, None, None, None, None)

    _root.packages = OrderedDict([('package2', _package2), ('package1', _package1)])

    @pytest.mark.package
    def test_package_tree(self):
        assert self._root is not None
        assert self._root.all_packages == [self._package11, self._package12, self._package2, self._package1]

    def test_public_interface(self):
        """
        Test public interface, which documented in docs/USAGE-PYTHON.md and people can use this attribute in python-code
        """
        package = self._package
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
