# -*- coding: utf-8 -*-
import fnmatch
import hashlib
import logging
import os
import shutil
from collections import OrderedDict

from artifactory import ArtifactoryPath

from crosspm.helpers.archive import Archive

# import only for TypeHint
try:
    from crosspm.helpers.downloader import Downloader  # noqa: F401
except ImportError:
    pass


class Package:
    def __init__(self, name, pkg, params, downloader, adapter, parser, params_found=None, params_found_raw=None,
                 stat=None, in_cache=False):
        self.name = name
        self.package_name = name
        self.packed_path = ''
        self.unpacked_path = ''
        self.duplicated = False
        self.packages = OrderedDict()

        self.pkg = pkg  # type: ArtifactoryPath
        # Someone use this internal object, do not remove  them :)
        self._pkg = self.pkg

        if isinstance(pkg, int):
            if pkg == 0:
                self._root = True

        self._raw = []
        self._root = False
        self._params_found = {}
        self._params_found_raw = {}
        self._not_cached = True
        self._log = logging.getLogger('crosspm')

        self._params = params
        self._adapter = adapter
        self._parser = parser
        self._downloader = downloader  # type: Downloader
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
        exists, dest_path = self._downloader.cache.exists_packed(package=self, pkg_path=self.packed_path,
                                                                 check_stat=not self._in_cache)
        unp_exists, unp_path = self._downloader.cache.exists_unpacked(package=self, pkg_path=self.unpacked_path)

        # Если архива нет, то и кешу доверять не стоит
        if not exists:
            unp_exists = False

        if exists and not self.packed_path:
            self.packed_path = dest_path

        if force or not exists:
            # _packed_path = self._packed_path
            dest_path_tmp = dest_path + ".tmp"
            if os.path.exists(dest_path_tmp):
                os.remove(dest_path_tmp)
            self._adapter.download_package(self._pkg, dest_path_tmp)
            os.rename(dest_path_tmp, dest_path)
            self.packed_path = dest_path
            # if not _packed_path:
            self._not_cached = True
        else:
            if unp_exists and not self.unpacked_path:
                self.unpacked_path = unp_path
                self._not_cached = False

        if self._not_cached and unp_exists:
            shutil.rmtree(unp_path, ignore_errors=True)

        return self.packed_path

    def get_file(self, file_name, unpack_force=True):
        if unpack_force:
            self.unpack()
        _dest_file = os.path.normpath(self.get_file_path(file_name))
        _dest_file = _dest_file if os.path.isfile(_dest_file) else None
        return _dest_file

    def get_file_path(self, file_name):
        _dest_file = os.path.join(self.unpacked_path, file_name)
        return _dest_file

    def find_dependencies(self, depslock_file_path, property_validate=True, deps_content=None):
        """
        Find all dependencies by package
        :param depslock_file_path:
        :param property_validate: for `root` packages we need check property, bad if we find packages from `lock` file,
        :param deps_content: HACK for use --dependencies-content and existed dependencies.txt.lock file
        we can skip validate part
        :return:
        """
        self._raw = [x for x in
                     self._downloader.common_parser.iter_packages_params(depslock_file_path, deps_content=deps_content)]
        self.packages = self._downloader.get_dependency_packages({'raw': self._raw},
                                                                 property_validate=property_validate)

    def find_usedby(self, depslock_file_path, property_validate=True):
        """
        Find all dependencies by package
        :param depslock_file_path:
        :param property_validate: for `root` packages we need check property, bad if we find packages from `lock` file,
        we can skip validate part
        :return:
        """
        if depslock_file_path is None:
            self._raw = [self._params]
            self._raw[0]['repo'] = None
            self._raw[0]['server'] = None
        else:
            self._raw = [x for x in self._downloader.common_parser.iter_packages_params(depslock_file_path)]
        self.packages = self._downloader.get_usedby_packages({'raw': self._raw},
                                                             property_validate=property_validate)

    def unpack(self, force=False):
        if self._downloader.solid(self):
            self.unpacked_path = self.packed_path
        else:
            exists, dest_path = self._downloader.cache.exists_unpacked(package=self, pkg_path=self.unpacked_path)
            if exists and not self.unpacked_path:
                self.unpacked_path = dest_path

            # if force or not exists:

            # if not dest_path:
            #     dest_path = self._downloader.unpacked_path
            # temp_path = os.path.realpath(os.path.join(dest_path, self._name))
            # _exists = os.path.exists(temp_path)
            if not self._not_cached:
                self.unpacked_path = dest_path if exists else ''  # temp_path if exists else ''
            if force or self._not_cached or (not exists):
                Archive.extract(self.packed_path, dest_path)  # temp_path)
                self.unpacked_path = dest_path  # temp_path
                self._not_cached = False

    def pack(self, src_path):
        Archive.create(self.packed_path, src_path)

    def print(self, level=0, output=None):
        def do_print(left):
            res_str = ''
            for out_item in output:
                for k, v in out_item.items():
                    cur_str = self.get_params(merged=True).get(k, '')
                    if not res_str:
                        cur_str = self._params.get(k, '')
                    if not res_str:
                        res_str = '{}{}'.format(left, cur_str)
                        continue
                    cur_format = ' {}'
                    if v > 0:
                        cur_format = '{:%s}' % (v if len(cur_str) <= v else v + len(left))
                    res_str += cur_format.format(cur_str)
                    break
            self._log.info(res_str)

        _sign = ' '
        if not self._root:
            if self.duplicated:
                _sign = '!'
            elif self.unpacked_path:
                _sign = '+'
            elif self.packed_path:
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
        """
        Get Package params
        :param param_list: name or list of parameters
        :param get_path:
        :param merged: if version splited, True return version in string
        :param raw:
        :return:
        """
        # Convert parameter name to list
        if param_list and isinstance(param_list, str):
            param_list = [param_list]
        if param_list and isinstance(param_list, (list, tuple)):
            result = {k: v for k, v in self._params_found.items() if k in param_list}
            result.update({k: v for k, v in self._params.items() if (k in param_list and k not in result)})
        else:
            result = {k: v for k, v in self._params_found.items()}
            result.update({k: v for k, v in self._params.items() if k not in result})
        if get_path:
            result['path'] = self.unpacked_path
        if merged:
            result.update(self._parser.merge_valued(result))
        if raw:
            result.update({k: v for k, v in self._params_found_raw.items()})
        return result

    def set_full_unique_name(self):
        self.name = self._parser.get_full_package_name(self)
        return self.name

    def get_name_and_path(self, name_only=False):
        if name_only:
            return self.name
        return self.name, self.unpacked_path

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

    @property
    def md5(self):
        try:
            return ArtifactoryPath.stat(self.pkg).md5
        except AttributeError:
            return md5sum(self.packed_path)


def md5sum(filename):
    """
    Calculates md5 hash of a file
    """
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()
