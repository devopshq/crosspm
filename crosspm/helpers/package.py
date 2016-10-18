# -*- coding: utf-8 -*-
import os

from crosspm.helpers.archive import Archive
from crosspm.helpers.exceptions import *


class Package(object):
    _packed_path = ''
    _unpacked_path = ''
    _packages = {}
    _raw = []
    _root = False
    _params_found = {}

    def __init__(self, name, pkg, params, downloader, adapter, parser, params_found=None):
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

    def download(self, dest_path, force=False):
        if force or not self._unpacked_path:
            dest_path = os.path.realpath(os.path.join(dest_path, self._name))
            self._packed_path = self._adapter.download_package(self._pkg, dest_path)
        return self._packed_path

    def get_file(self, file_name, temp_path=None):
        if not temp_path:
            temp_path = self._downloader.temp_path
        temp_path = os.path.realpath(os.path.join(temp_path, self._name))

        _dest_file = Archive.extract_file(self._packed_path, temp_path, file_name)

        return _dest_file

    def find_dependencies(self, depslock_file_path):
        self._raw = [x for x in self._parser.iter_packages_params(depslock_file_path)]
        self._packages = self._downloader.get_packages(self._raw)

    def unpack(self, dest_path=''):
        if not dest_path:
            dest_path = self._downloader.unpacked_path
        temp_path = os.path.realpath(os.path.join(dest_path, self._name))
        try:
            Archive.extract(self._packed_path, temp_path)
            self._unpacked_path = temp_path
        except:
            pass

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
            print_stdout(res_str)

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
        for _pkg_name, _pkg in self._packages.items():
            if not _pkg:
                _left = '{}-'.format(' ' * 4 * (level + 1))
                print_stdout('{}{}'.format(_left, _pkg_name))
            else:
                _pkg.print(level + 1, output)
        if self._root:
            print_stdout('')

    def get_name_and_path(self, name_only=False):
        if name_only:
            return self._name
        return self._name, self._unpacked_path

    def get_params(self, param_list):
        result = {k: v for k, v in self._params_found.items() if k in param_list}
        result.update({k: v for k, v in self._params.items() if (k in param_list and k not in result)})
        return result

    def set_full_unique_name(self):
        self._name = self._parser.get_full_package_name(self)
        return self._name
