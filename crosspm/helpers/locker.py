# -*- coding: utf-8 -*-
import os

from crosspm.helpers.config import CROSSPM_DEPENDENCY_FILENAME
from crosspm.helpers.content import DependenciesContent
from crosspm.helpers.downloader import Downloader
from crosspm.helpers.output import Output


class Locker(Downloader):
    def __init__(self, config, do_load, recursive):
        # TODO: revise logic to allow recursive search without downloading
        super(Locker, self).__init__(config, do_load, recursive)

        if not getattr(config, 'deps_path', ''):
            config.deps_path = config.deps_file_name or CROSSPM_DEPENDENCY_FILENAME

        deps_path = config.deps_path
        if deps_path.__class__ is DependenciesContent:
            # HACK
            pass
            self._deps_path = deps_path
        else:
            deps_path = config.deps_path.strip().strip('"').strip("'")
            self._deps_path = os.path.realpath(os.path.expanduser(deps_path))

    def lock_packages(self):
        """
        Lock packages. Downloader search packages
        """

        if len(self._root_package.packages) == 0:
            self.search_dependencies(self._deps_path)

        self._log.info('Writing lock file [{}]'.format(self._depslock_path))

        output_params = {
            'out_format': 'lock',
            'output': self._depslock_path,
        }
        Output(config=self._config).write_output(output_params, self._root_package.packages)
        self._log.info('Done!')

    def entrypoint(self, *args, **kwargs):
        self.lock_packages(*args, **kwargs)
