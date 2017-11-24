# -*- coding: utf-8 -*-
import fnmatch
import logging
import os
import shutil
from collections import OrderedDict

from crosspm.helpers.archive import Archive


class Package:
    def __init__(self, name, pkg, params, downloader, adapter, parser, params_found=None, params_found_raw=None,
                 stat=None, in_cache=False):
        self._packed_path = ''
        self._unpacked_path = ''
        self.packages = OrderedDict()
        self._raw = []
        self._root = False
        self._params_found = {}
        self._params_found_raw = {}
        self._not_cached = True
        self._log = logging.getLogger('crosspm')
        if isinstance(pkg, int):
            if pkg == 0:
                self._root = True
        self.name = name
        self.package_name = name  # unique name (* column)
        self.duplicated = False
        self._pkg = pkg
        self._params = params
        self._adapter = adapter
        self._parser = parser
        self._downloader = downloader
        self._in_cache = in_cache
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
        exists, dest_path = self._downloader.cache.exists_packed(package=self, pkg_path=self._packed_path,
                                                                 check_stat=not self._in_cache)
        if exists and not self._packed_path:
            self._packed_path = dest_path

        unp_exists, unp_path = self._downloader.cache.exists_unpacked(package=self, pkg_path=self._unpacked_path)

        if force or not exists:
            # _packed_path = self._packed_path
            dest_path_tmp = dest_path + ".tmp"
            if os.path.exists(dest_path_tmp):
                os.remove(dest_path_tmp)
            self._adapter.download_package(self._pkg, dest_path_tmp)
            os.rename(dest_path_tmp, dest_path)
            self._packed_path = dest_path
            # if not _packed_path:
            self._not_cached = True
        else:
            if unp_exists and not self._unpacked_path:
                self._unpacked_path = unp_path
                self._not_cached = False

        if self._not_cached and unp_exists:
            shutil.rmtree(unp_path, ignore_errors=True)

        return self._packed_path

    def get_file(self, file_name):
        self.unpack()
        _dest_file = os.path.join(self._unpacked_path, file_name)
        _dest_file = _dest_file if os.path.isfile(_dest_file) else None

        return _dest_file

    def find_dependencies(self, depslock_file_path):
        self._raw = [x for x in self._parser.iter_packages_params(depslock_file_path)]
        self.packages = self._downloader.get_dependency_packages({'raw': self._raw})

    def unpack(self, force=False):
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
            if self.duplicated:
                _sign = '!'
            elif self._unpacked_path:
                _sign = '+'
            elif self._packed_path:
                _sign = '>'
            else:
                _sign = '-'
        _left = '{}{}'.format(' ' * 4 * level, _sign)
        do_print(_left)
        for _pkg_name in self.packages:
            _pkg = self.packages[_pkg_name]
            if not _pkg:
                _left = '{}-'.format(' ' * 4 * (level + 1))
                self._log.info('{}{}'.format(_left, _pkg_name))
            else:
                _pkg.print(level + 1, output)
        if self._root:
            self._log.info('')

    def get_params(self, param_list=None, get_path=False, merged=False, raw=False):
        if param_list and isinstance(param_list, str):
            result = {param_list: self.name}
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
        self.name = self._parser.get_full_package_name(self)
        return self.name

    def get_none_packages(self):
        """
        Get packages with None (not founded), recursively
        """
        not_found = set()
        for package_name, package in self.packages.items():
            if package is None:
                not_found.add(package_name)
            else:
                if package.packages:
                    not_found = not_found | package.get_none_packages()
        return not_found

    @property
    def all_packages(self):
        packages = []
        for package in self.packages.values():
            if package:
                packages.extend(package.all_packages)
        packages.extend(self.packages.values())
        return packages

    def ext(self, check_ext):
        if self._pkg:
            if not isinstance(check_ext, (list, tuple)):
                check_ext = [check_ext]
            name = self._adapter.get_package_filename(self._pkg)
            if any((fnmatch.fnmatch(name, x) or fnmatch.fnmatch(name, '*%s' % x)) for x in check_ext):
                return True
        return False
