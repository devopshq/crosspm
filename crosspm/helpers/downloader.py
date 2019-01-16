# -*- coding: utf-8 -*-
import logging
import os
from collections import OrderedDict, defaultdict

from crosspm.helpers.config import CROSSPM_DEPENDENCY_FILENAME, CROSSPM_DEPENDENCY_LOCK_FILENAME, Config  # noqa
from crosspm.helpers.content import DependenciesContent
from crosspm.helpers.exceptions import *
from crosspm.helpers.package import Package
from crosspm.helpers.parser import Parser


def update_progress(msg, progress):
    sys.stderr.write('\r{0} [{1:10}] {2}%'.format(msg, '#' * int(float(progress) / 10.0), int(progress)))
    sys.stderr.flush()


class Command(object):
    def entrypoint(self, *args, **kwargs):
        assert NotImplemented


class Downloader(Command):
    def __init__(self, config, do_load, recursive):
        self._log = logging.getLogger('crosspm')
        self._config = config  # type: Config
        self.cache = config.cache
        self.solid = config.solid
        self.common_parser = Parser('common', {}, config)
        self._root_package = Package('<root>', 0, {self._config.name_column: '<root>'}, self, None,
                                     self.common_parser)
        self.recursive = recursive

        if not config.deps_path:
            config.deps_path = \
                config.deps_file_name if config.deps_file_name else CROSSPM_DEPENDENCY_FILENAME
        deps_path = config.deps_path
        if deps_path.__class__ is DependenciesContent:
            # HACK
            pass
            self._deps_path = deps_path
        else:
            deps_path = config.deps_path.strip().strip('"').strip("'")
            self._deps_path = os.path.realpath(os.path.expanduser(deps_path))

        if not config.depslock_path:
            config.depslock_path = \
                config.deps_lock_file_name if config.deps_lock_file_name else CROSSPM_DEPENDENCY_LOCK_FILENAME
        depslock_path = config.depslock_path
        if depslock_path.__class__ is DependenciesContent:
            # HACK
            self._depslock_path = depslock_path
        else:
            depslock_path = depslock_path.strip().strip('"').strip("'")
            self._depslock_path = os.path.realpath(os.path.expanduser(depslock_path))

        self.do_load = do_load

    # Get list of all packages needed to resolve all the dependencies.
    # List of Package class instances.
    def get_dependency_packages(self, list_or_file_path=None, property_validate=True):
        """
        :param list_or_file_path:
        :param property_validate: for `root` packages we need check property, bad if we find packages from `lock` file,
        we can skip validate part
        """
        if list_or_file_path is None:
            list_or_file_path = self._depslock_path
            if not os.path.isfile(list_or_file_path):
                list_or_file_path = self._deps_path

        _packages = OrderedDict()
        if isinstance(list_or_file_path, str):
            self._log.info('Reading dependencies ... [%s]', list_or_file_path)
        for i, _src in enumerate(self._config.sources()):
            if i > 0:
                self._log.info('')
                self._log.info('Next source ...')
            _found_packages = _src.get_packages(self, list_or_file_path, property_validate)
            _packages.update(
                OrderedDict([(k, v) for k, v in _found_packages.items() if _packages.get(k, None) is None]))
            if not self._config.no_fails:
                if isinstance(list_or_file_path, (list, tuple)):
                    list_or_file_path = [x for x in list_or_file_path if
                                         _packages.get(x[self._config.name_column], None) is None]
                elif isinstance(list_or_file_path, dict) and isinstance(list_or_file_path.get('raw', None), list):
                    list_or_file_path['raw'] = [x for x in list_or_file_path['raw'] if
                                                _packages.get(x[self._config.name_column], None) is None]

        return _packages

    def get_usedby_packages(self, list_or_file_path=None, property_validate=True):
        """

        :param list_or_file_path:
        :param property_validate: for `root` packages we need check property, bad if we find packages from `lock` file,
        we can skip validate part
        :return:
        """
        if list_or_file_path is None:
            list_or_file_path = self._depslock_path
            if not os.path.isfile(list_or_file_path):
                list_or_file_path = self._deps_path

        _packages = OrderedDict()
        if isinstance(list_or_file_path, str):
            self._log.info('Reading dependencies ... [%s]', list_or_file_path)
        for i, _src in enumerate(self._config.sources()):
            if i > 0:
                self._log.info('')
                self._log.info('Next source ...')
            _found_packages = _src.get_usedby(self, list_or_file_path, property_validate)
            _packages.update(
                OrderedDict([(k, v) for k, v in _found_packages.items() if _packages.get(k, None) is None]))
            if not self._config.no_fails:
                if isinstance(list_or_file_path, (list, tuple)):
                    list_or_file_path = [x for x in list_or_file_path if
                                         _packages.get(x[self._config.name_column], None) is None]
                elif isinstance(list_or_file_path, dict) and isinstance(list_or_file_path.get('raw', None), list):
                    list_or_file_path['raw'] = [x for x in list_or_file_path['raw'] if
                                                _packages.get(x[self._config.name_column], None) is None]

        return _packages

    # Download packages or just unpack already loaded (it's up to adapter to decide)
    def download_packages(self, depslock_file_path=None):
        if depslock_file_path is None:
            depslock_file_path = self._depslock_path
        if depslock_file_path.__class__ is DependenciesContent:
            # HACK для возможности проставления контента файла, а не пути
            pass
        elif isinstance(depslock_file_path, str):
            if not os.path.isfile(depslock_file_path):
                depslock_file_path = self._deps_path

        deps_content = self._deps_path if isinstance(self._deps_path, DependenciesContent) else None
        self.search_dependencies(depslock_file_path, deps_content=deps_content)

        if self.do_load:
            self._log.info('Unpack ...')

            total = len(self._root_package.all_packages)
            for i, _pkg in enumerate(self._root_package.all_packages):
                update_progress('Download/Unpack:', float(i) / float(total) * 100.0)
                if _pkg.download():  # self.packed_path):
                    _pkg.unpack()  # self.unpacked_path)

            update_progress('Download/Unpack:', 100)
            print_stdout('')
            self._log.info('Done!')
            sys.stdout.write('\n')
            sys.stdout.write('\n')
            sys.stdout.flush()

            if self._config.lock_on_success:
                from crosspm.helpers.locker import Locker
                depslock_path = os.path.realpath(
                    os.path.join(os.path.dirname(depslock_file_path), self._config.deps_lock_file_name))
                Locker(self._config, do_load=self.do_load, recursive=self.recursive).lock_packages(
                    depslock_file_path, depslock_path, packages=self._root_package.packages)

        return self._root_package.all_packages

    def entrypoint(self, *args, **kwargs):
        self.download_packages(*args, **kwargs)

    def search_dependencies(self, depslock_file_path, deps_content=None):
        self._log.info('Check dependencies ...')
        self._root_package.find_dependencies(depslock_file_path, property_validate=True, deps_content=deps_content, )
        self._log.info('')
        self.set_duplicated_flag()
        self._log.info('Dependency tree:')
        self._root_package.print(0, self._config.output('tree', [{self._config.name_column: 0}]))
        self.check_unique(self._config.no_fails)
        self.check_not_found()

    def check_not_found(self):
        _not_found = self.get_not_found_packages()
        if _not_found:
            raise CrosspmException(
                CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
                'Some package(s) not found: {}'.format(', '.join(_not_found))
            )

    def get_not_found_packages(self):
        return self._root_package.get_none_packages()

    def add_package(self, pkg_name, package):
        _added = False
        if package is not None:
            _added = True
        return _added, package

    def set_duplicated_flag(self):
        """
        For all package set flag duplicated, if it's not unique package
        :return:
        """
        package_by_name = defaultdict(list)

        for package1 in self._root_package.all_packages:
            if package1 is None:
                continue
            pkg_name = package1.package_name
            param_list = self._config.get_fails('unique', {})
            params1 = package1.get_params(param_list)
            for package2 in package_by_name[pkg_name]:
                params2 = package2.get_params(param_list)
                for x in param_list:
                    # START HACK for cached archive
                    param1 = params1[x]
                    param2 = params2[x]
                    if isinstance(param1, list):
                        param1 = [str(x) for x in param1]
                    if isinstance(param2, list):
                        param2 = [str(x) for x in param2]
                    # END

                    if str(param1) != str(param2):
                        package1.duplicated = True
                        package2.duplicated = True
            package_by_name[pkg_name].append(package1)

    def check_unique(self, no_fails):
        if no_fails:
            return
        not_unique = set(x.package_name for x in self._root_package.all_packages if x and x.duplicated)
        if not_unique:
            raise CrosspmException(
                CROSSPM_ERRORCODE_MULTIPLE_DEPS,
                'Multiple versions of package "{}" found in dependencies.\n'
                'See dependency tree in log (package with exclamation mark "!")'.format(
                    ', '.join(not_unique)),
            )

    def get_raw_packages(self):
        """
        Get all packages
        :return: list of all packages
        """
        return self._root_package.all_packages

    def get_tree_packages(self):
        """
        Get all packages, with hierarchy
        :return: list of first level packages, with child
        """
        return self._root_package.packages
