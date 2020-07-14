# -*- coding: utf-8 -*-
import os

from crosspm.helpers.config import CROSSPM_DEPENDENCY_FILENAME
from crosspm.helpers.content import DependenciesContent
from crosspm.helpers.downloader import Downloader
from crosspm.helpers.output import Output
from crosspm.helpers.parser import Parser


class Locker(Downloader):
    def __init__(self, config, do_load, recursive, parser_cls = Parser):
        # TODO: revise logic to allow recursive search without downloading
        super(Locker, self).__init__(config, do_load, recursive, parser_cls)

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

    def lock_packages(self, deps_file_path=None, depslock_file_path=None, packages=None):
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

        if packages is None:
            self.search_dependencies(deps_file_path)
        else:
            self._root_package.packages = packages

        self._log.info('Writing lock file [{}]'.format(depslock_file_path))

        output_params = {
            'out_format': 'lock',
            'output': depslock_file_path,
        }
        Output(config=self._config).write_output(output_params, self._root_package.packages)
        self._log.info('Done!')

    def entrypoint(self, *args, **kwargs):
        self.lock_packages(*args, **kwargs)
