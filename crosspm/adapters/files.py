# -*- coding: utf-8 -*-
import json
import shutil
from datetime import datetime
import time

import pathlib

from crosspm.adapters.common import BaseAdapter
from crosspm.helpers.exceptions import *
from crosspm.helpers.package import Package
import os
import requests

CHUNK_SIZE = 1024

setup = {
    "name": [
        "files",
    ],
}


# class PureFilesPath(pathlib.PurePath):
#     """
#     A class to work with Files paths that doesn't connect
#     to any server. I.e. it supports only basic path
#     operations.
#     """
#     _flavour = pathlib._posix_flavour
#     __slots__ = ()
#

class FilesPath(pathlib.Path):  # , PureFilesPath):
    def glob(self, pattern):
        return super(FilesPath, self).glob(pattern)

    def rglob(self, pattern):
        return super(FilesPath, self).rglob(pattern)

    def __new__(cls, *args, **kwargs):
        cls = WindowsPath if os.name == 'nt' else PosixPath
        obj = pathlib.Path.__new__(cls, *args, **kwargs)
        return obj

    @property
    def properties(self):
        """
        Fetch artifact properties
        """
        return {}

    @properties.setter
    def properties(self, properties):
        self.del_properties(self.properties, recursive=False)
        self.set_properties(properties, recursive=False)

    @properties.deleter
    def properties(self):
        self.del_properties(self.properties, recursive=False)

    def set_properties(self, properties, recursive=True):
        """
        Adds new or modifies existing properties listed in properties

        properties - is a dict which contains the property names and values to set.
                     Property values can be a list or tuple to set multiple values
                     for a key.
        recursive  - on folders property attachment is recursive by default. It is
                     possible to force recursive behavior.
        """
        if not properties:
            return False

        return True  # self._accessor.set_properties(self, properties, recursive)

    def del_properties(self, properties, recursive=None):
        """
        Delete properties listed in properties

        properties - iterable contains the property names to delete. If it is an
                     str it will be casted to tuple.
        recursive  - on folders property attachment is recursive by default. It is
                     possible to force recursive behavior.
        """
        return True  # self._accessor.del_properties(self, properties, recursive)


class PosixPath(FilesPath, pathlib.PurePosixPath):
    __slots__ = ()


class WindowsPath(FilesPath, pathlib.PureWindowsPath):
    __slots__ = ()

    def owner(self):
        raise NotImplementedError("Path.owner() is unsupported on this system")

    def group(self):
        raise NotImplementedError("Path.group() is unsupported on this system")


class Adapter(BaseAdapter):
    def get_packages(self, source, parser, downloader, list_or_file_path):
        _pkg_name_col = self._config.name_column
        _packages_found = {}
        _pkg_name_old = ""
        for _paths in parser.get_paths(list_or_file_path, source):
            _packages = []
            _params_found = {}
            _pkg_name = _paths['params'][_pkg_name_col]
            if _pkg_name != _pkg_name_old:
                _pkg_name_old = _pkg_name
                self._log.info(
                    '{}: {}'.format(_pkg_name, {k: v for k, v in _paths['params'].items() if k != _pkg_name_col}))
            last_error = ''
            for _path in _paths['paths']:
                _path_fixed, _path_pattern = parser.split_fixed_pattern(_path)
                _repo_paths = FilesPath(_path_fixed)
                try:
                    for _repo_path in _repo_paths.glob(_path_pattern):
                        _mark = 'found'
                        _matched, _params = parser.validate_path(str(_repo_path), _paths['params'])
                        if _matched:
                            _params_found[_repo_path] = {k: v for k, v in _params.items()}
                            _mark = 'match'
                            _valid, _params = parser.validate(_repo_path.properties, 'properties', _paths['params'],
                                                              return_params=True)
                            if _valid:
                                _mark = 'valid'
                                _packages += [_repo_path]
                                _params_found[_repo_path].update({k: v for k, v in _params.items()})
                                _params_found[_repo_path]['filename'] = str(_repo_path.name)
                        self._log.debug('  {}: {}'.format(_mark, str(_repo_path)))
                except RuntimeError as e:
                    try:
                        err = json.loads(e.args[0])
                    except:
                        err = {}
                    if isinstance(err, dict):
                        # TODO: Check errors
                        # e.args[0] = '''{
                        #                   "errors" : [ {
                        #                     "status" : 404,
                        #                     "message" : "Not Found"
                        #                   } ]
                        #                 }'''
                        for error in err.get('errors', []):
                            err_status = error.get('status', -1)
                            err_msg = error.get('message', '')
                            if err_status == 401:
                                msg = 'Authentication error[{}]{}'.format(err_status,
                                                                          (': {}'.format(err_msg)) if err_msg else '')
                            elif err_status == 404:
                                msg = last_error
                            else:
                                msg = 'Error[{}]{}'.format(err_status,
                                                           (': {}'.format(err_msg)) if err_msg else '')
                            if last_error != msg:
                                self._log.error(msg)
                            last_error = msg

            _package = None
            if _packages:
                _packages = parser.filter_one(_packages, _paths['params'], _params_found)
                if type(_packages) is dict:
                    _packages = [_packages]

                if len(_packages) == 1:
                    _stat_pkg = self.pkg_stat(_packages[0]['path'])

                    _params_tmp = _params_found.get(_packages[0]['path'], {})
                    _params_tmp.update({k: v for k, v in _packages[0]['params'].items() if k not in _params_tmp})
                    _package = Package(_pkg_name, _packages[0]['path'], _paths['params'], downloader, self, parser,
                                       _params_tmp, _stat_pkg)
                    _mark = 'chosen'
                    self._log.info('  {}: {}'.format(_mark, str(_packages[0]['path'])))

                elif len(_packages) > 1:
                    raise CrosspmException(
                        CROSSPM_ERRORCODE_MULTIPLE_DEPS,
                        'Multiple instances found for package [{}] not found.'.format(_pkg_name)
                    )
                else:
                    # Package not found: may be error, but it could be in other source.
                    pass
            else:
                # Package not found: may be error, but it could be in other source.
                pass

            if (_package is not None) or (not self._config.no_fails):
                _added, _package = downloader.add_package(_pkg_name, _package)
            else:
                _added = False
            if _package is not None:
                _pkg_name = _package.get_name_and_path(True)
            if _added or (_package is not None):
                if (_package is not None) or (not self._config.no_fails):
                    if (_package is not None) or (_packages_found.get(_pkg_name, None) is None):
                        _packages_found[_pkg_name] = _package

            if _added and (_package is not None):
                if downloader.do_load:
                    _package.download()

                    _deps_file = _package.get_file(self._config.deps_lock_file_name, downloader.cache.temp_path)
                    if _deps_file:
                        _package.find_dependencies(_deps_file)
                    elif self._config.deps_file_name:
                        _deps_file = _package.get_file(self._config.deps_file_name, downloader.cache.temp_path)
                        if _deps_file and os.path.isfile(_deps_file):
                            _package.find_dependencies(_deps_file)

        return _packages_found

    def pkg_stat(self, package):
        _stat_attr = {'ctime': 'st_atime',
                      'mtime': 'st_mtime',
                      'size': 'st_size'}
        _stat_pkg = os.stat(str(package))
        _stat_pkg = {k: getattr(_stat_pkg, v, None) for k, v in _stat_attr.items()}
        return _stat_pkg

    def download_package(self, package, dest_path):
        dest_dir = os.path.dirname(dest_path)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        elif os.path.exists(dest_path):
            os.remove(dest_path)

        try:
            _stat_pkg = self.pkg_stat(package)
            shutil.copyfile(str(package), dest_path)
            os.utime(dest_path, (_stat_pkg['ctime'], _stat_pkg['mtime']))

        except Exception as e:
            code = CROSSPM_ERRORCODE_SERVER_CONNECT_ERROR
            msg = 'FAILED to download package {} at url: [{}]'.format(
                package.name,
                str(package),
            )
            raise CrosspmException(code, msg) from e

        return dest_path

    def get_package_filename(self, package):
        if isinstance(package, FilesPath):
            return package.name
        return ''

    def get_package_path(self, package):
        if isinstance(package, FilesPath):
            return str(package)
        return ''
