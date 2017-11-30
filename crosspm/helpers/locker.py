# -*- coding: utf-8 -*-
import os
from collections import OrderedDict

from crosspm.helpers.config import CROSSPM_DEPENDENCY_FILENAME
from crosspm.helpers.downloader import Downloader
from crosspm.helpers.output import Output


class Locker(Downloader):
    def __init__(self, config):
        # TODO: revise logic to allow recursive search without downloading
        super(Locker, self).__init__(config, do_load=False or config.recursive)

        if not getattr(config, 'deps_path', ''):
            config.deps_path = config.deps_file_name or CROSSPM_DEPENDENCY_FILENAME
        deps_path = config.deps_path.strip().strip('"').strip("'")
        self._deps_path = os.path.realpath(os.path.expanduser(deps_path))

    def lock_packages(self, deps_file_path=None, depslock_file_path=None, search_before=True):
        """
        Lock packages. Downloader search packages
        """
        if deps_file_path is None:
            deps_file_path = self._deps_path
        if depslock_file_path is None:
            depslock_file_path = self._depslock_path
        if deps_file_path == depslock_file_path:
            depslock_file_path += '.lock'
            # raise CrosspmException(
            #     CROSSPM_ERRORCODE_WRONG_ARGS,
            #     'Dependencies and Lock files are same: "{}".'.format(deps_file_path),
            # )

        if search_before:
            self.search_dependencies(deps_file_path)

        self._log.info('Writing lock file [{}]'.format(depslock_file_path))

        output_params = {
            'out_format': 'lock',
            'output': depslock_file_path,
        }
        Output(config=self._config).write(output_params, self._root_package.packages)
        self._log.info('Done!')
        return self._root_package.packages
