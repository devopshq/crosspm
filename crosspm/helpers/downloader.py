# -*- coding: utf-8 -*-
import os
import sys
import logging

from crosspm.helpers.package import Package
from crosspm.helpers.parser import Parser
from crosspm.helpers.output import make_output
from crosspm.helpers.exceptions import *


# TODO: Check if it is really necessary:
def print_stderr(*args, **kwargs):
    kwargs.update({'file': sys.stderr})
    print(*args, **kwargs)


class Downloader(object):
    # _log = None
    # _config = None
    # _params = {}
    # _package = None
    _packages = {}

    def __init__(self, config, params):
        self._log = logging.getLogger(__name__)
        self._config = config
        self._params = params
        self._root_package = Package('<root>', 0, {}, self, None, Parser('<root>', {}, config))

        self._cache_path = config.get_crosspm_cache_root()
        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        self.packed_path = os.path.realpath(os.path.join(self._cache_path, 'archive'))
        self.unpacked_path = os.path.realpath(os.path.join(self._cache_path, 'cache'))
        self.temp_path = os.path.realpath(os.path.join(self._cache_path, 'tmp'))

        if 'depslock_path' in params:
            self._params['depslock_path'] = os.path.realpath(params['depslock_path'])

    # Get list of all packages needed to resolve all the dependencies.
    # List of Package class instances.
    def get_packages(self, list_or_file_path=None):
        if list_or_file_path is None:
            list_or_file_path = self._params['depslock_path']

        _packages = {}
        if type(list_or_file_path) is str:
            self._log.info('Reading dependencies ... [%s]', list_or_file_path)
        for _src in self._config.sources():
            _found_packages = _src.get_packages(self, list_or_file_path)
            _packages.update({k: v for k, v in _found_packages.items() if (v is not None) or (k not in _packages)})

        return _packages

    # Download packages or just unpack already loaded (it's up to adapter to decide)
    def download_packages(self, depslock_file_path=None):
        if depslock_file_path is None:
            depslock_file_path = self._params['depslock_path']

        self._packages = {}
        self._root_package.find_dependencies(depslock_file_path)

        self._log.info('Check dependencies ...')

        self._root_package.print()

        # TODO: Implement real dependencies checker
        _not_found = sum(1 if _pkg is None else 0 for _pkg in self._packages.values())

        if _not_found:
            raise CrosspmException(
                CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
                'Some package(s) not found.'
                )

        self._log.info('Downloading ...')

        for _pkg in self._packages.values():
            if _pkg.download(self.packed_path):
                _pkg.unpack(self.unpacked_path)

        make_output(
            self._params['out_format'],
            self._params['output'],
            self._params['out_prefix'],
            self._packages,
        )

        self._log.info('Done!')

    def add_package(self, pkg_name, package):
        _added = False
        if pkg_name in self._packages:
            if self._packages[pkg_name] is None:
                self._packages[pkg_name] = package
                _added = True
        else:
            self._packages[pkg_name] = package
            _added = True
        return _added
