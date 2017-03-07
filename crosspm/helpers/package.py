# -*- coding: utf-8 -*-
import logging
import os
import fnmatch

import shutil
from crosspm.helpers.archive import Archive
from crosspm.helpers.exceptions import *


class Package(object):
    _packed_path = ''
    _unpacked_path = ''
    packages = {}
    _raw = []
    _root = False
    _params_found = {}
    _params_found_raw = {}
    stat = None
    _not_cached = True

    def __init__(self, name, pkg, params, downloader, adapter, parser, params_found=None, params_found_raw=None, stat=None):
        self._log = logging.getLogger('crosspm')
        if type(pkg) is int:
            if pkg == 0:
                self._root = True
        self._name = name
        self._pkg = pkg
        self._params = params
        self._adapter = adapter
        self._parser = parser
        self._downloader = downloader
        if params_found:
            self._params_found = params_found
        if params_found_raw:
            self._params_found_raw = params_found_raw
        self.stat = stat

    def download(self, force=False):
        """
        Download file containing this package.
        :param force: Force download even if it seems file already exists
        :return: Full path with filename of downloaded package file.
        """
        exists, dest_path = self._downloader.cache.exists_packed(package=self, pkg_path=self._packed_path)
        if exists and not self._packed_path:
            self._packed_path = dest_path

        unp_exists, unp_path = self._downloader.cache.exists_unpacked(package=self, pkg_path=self._unpacked_path)

        if force or not exists:
            # _packed_path = self._packed_path
            self._packed_path = self._adapter.download_package(self._pkg, dest_path)
            # if not _packed_path:
            self._not_cached = True
        else:
            if unp_exists and not self._unpacked_path:
                self._unpacked_path = unp_path
                self._not_cached = False

        if self._not_cached and unp_exists:
            shutil.rmtree(unp_path, ignore_errors=True)

        return self._packed_path

    def get_file(self, file_name, temp_path=None):
        if not temp_path:
            temp_path = self._downloader.temp_path
        temp_path = os.path.realpath(os.path.join(temp_path, self._name))

        _dest_file = Archive.extract_file(self._packed_path, temp_path, file_name)

        return _dest_file

    def find_dependencies(self, depslock_file_path):
        self._raw = [x for x in self._parser.iter_packages_params(depslock_file_path)]
        self.packages = self._downloader.get_packages(self._raw)

    def unpack(self, dest_path='', force=False):
        if self._downloader.solid(self):
            self._unpacked_path = self._packed_path
        else:
            exists, dest_path = self._downloader.cache.exists_unpacked(package=self, pkg_path=self._unpacked_path)
            if exists and not self._unpacked_path:
                self._unpacked_path = dest_path

            # if force or not exists:

            # if not dest_path:
            #     dest_path = self._downloader.unpacked_path
            # temp_path = os.path.realpath(os.path.join(dest_path, self._name))
            # _exists = os.path.exists(temp_path)
            if not self._not_cached:
                self._unpacked_path = dest_path if exists else ''  # temp_path if exists else ''
            if force or self._not_cached or (not exists):
                Archive.extract(self._packed_path, dest_path)  # temp_path)
                self._unpacked_path = dest_path  # temp_path
                self._not_cached = False

    def pack(self, src_path):
        Archive.create(self._packed_path, src_path)

    def print(self, level=0, output=None):
        def do_print(left):
            res_str = ''
            for out_item in output:
                for k, v in out_item.items():
                    cur_str = self._params_found.get(k, '')
                    if not res_str:
                        cur_str = self._params.get(k, '')
                    if not res_str:
                        cur_str = '{}{} '.format(left, cur_str)
                    cur_format = '{}'
                    if v > 0:
                        cur_format = '{:%s}' % (v if len(cur_str) <= v else v + len(left))
                    res_str += cur_format.format(cur_str)
                    break
            self._log.info(res_str)

        _sign = ' '
        if not self._root:
            if self._unpacked_path:
                _sign = '+'
            elif self._packed_path:
                _sign = '>'
            else:
                _sign = '-'
        _left = '{}{}'.format(' ' * 4 * level, _sign)
        do_print(_left)
        for _pkg_name, _pkg in self.packages.items():
            if not _pkg:
                _left = '{}-'.format(' ' * 4 * (level + 1))
                self._log.info('{}{}'.format(_left, _pkg_name))
            else:
                _pkg.print(level + 1, output)
        if self._root:
            self._log.info('')

    def get_name_and_path(self, name_only=False):
        if name_only:
            return self._name
        return self._name, self._unpacked_path

    def get_params(self, param_list=None, get_path=False, merged=False, raw=False):
        if param_list and isinstance(param_list, str):
            result = {param_list: self._name}
        elif param_list and isinstance(param_list, (list, tuple)):
            result = {k: v for k, v in self._params_found.items() if k in param_list}
            result.update({k: v for k, v in self._params.items() if (k in param_list and k not in result)})
        else:
            result = {k: v for k, v in self._params_found.items()}
            result.update({k: v for k, v in self._params.items() if k not in result})
        if get_path:
            result['path'] = self._unpacked_path
        if merged:
            result.update(self._parser.merge_valued(result))
        if raw:
            result.update({k: v for k, v in self._params_found_raw.items()})
        return result

    def set_full_unique_name(self):
        self._name = self._parser.get_full_package_name(self)
        return self._name

    def ext(self, check_ext):
        if self._pkg:
            if not isinstance(check_ext, (list, tuple)):
                check_ext = [check_ext]
            name = self._adapter.get_package_filename(self._pkg)
            if any((fnmatch.fnmatch(name, x) or fnmatch.fnmatch(name, '*%s' % x)) for x in check_ext):
                return True
        return False
