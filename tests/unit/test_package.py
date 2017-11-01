# -*- coding: utf-8 -*-
from collections import OrderedDict

import pytest

from crosspm.helpers.package import Package


class TestPackage():
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
