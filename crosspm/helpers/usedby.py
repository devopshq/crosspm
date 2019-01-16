# -*- coding: utf-8 -*-

from crosspm.helpers.locker import Locker


class Usedby(Locker):
    def __init__(self, config, do_load, recursive):
        # Ignore do_load flag
        super(Usedby, self).__init__(config, False, recursive)

    def usedby_packages(self, deps_file_path=None, depslock_file_path=None, packages=None):
        """
        Lock packages. Downloader search packages
        """
        if deps_file_path is None:
            deps_file_path = self._deps_path
        if depslock_file_path is None:
            depslock_file_path = self._depslock_path
        if deps_file_path == depslock_file_path:
            depslock_file_path += '.lock'

        if packages is None:
            self.search_dependencies(deps_file_path)
        else:
            self._root_package.packages = packages
        self._log.info('Done!')

    def search_dependencies(self, depslock_file_path):
        self._log.info('Check dependencies ...')
        self._root_package.find_usedby(depslock_file_path, property_validate=True)
        self._log.info('')
        self._log.info('Dependency tree:')
        self._root_package.print(0, self._config.output('tree', [{self._config.name_column: 0}]))

    def entrypoint(self, *args, **kwargs):
        self.usedby_packages(*args, **kwargs)
