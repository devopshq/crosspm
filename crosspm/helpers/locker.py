# -*- coding: utf-8 -*-
from typing import Optional, Dict
from crosspm.helpers.package import Package
from crosspm.helpers.downloader import Downloader
from crosspm.helpers.output import Output


class Locker(Downloader):
    def __init__(self, config, do_load, recursive):
        # TODO: revise logic to allow recursive search without downloading
        super(Locker, self).__init__(config, do_load, recursive)

    def lock_packages(self, packages: Optional[Dict[str, Package]] = None):
        """
        Lock packages. Downloader search packages
        """

        if packages:
            self._root_package.packages = packages

        if len(self._root_package.packages) == 0:
            self.search_dependencies(self._config.deps_file_path, self._config.deps_content)

        output_params = {
            'out_format': 'lock',
            'output': self._config.deps_lock_file_path,
        }
        Output(config=self._config).write_output(output_params, self._root_package.packages)
        self._log.info('Done!')

    def entrypoint(self, *args, **kwargs):
        self.lock_packages(*args, **kwargs)
