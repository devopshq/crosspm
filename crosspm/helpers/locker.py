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

    # Download packages or just unpack already loaded (it's up to adapter to decide)
    def lock_packages(self, deps_file_path=None, depslock_file_path=None, search_before=True):
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
        text = ''
        tmp_packages = OrderedDict()
        columns = self._config.get_columns()
        widths = {}
        for _pkg in self._root_package.packages.values():
            _pkg_name = _pkg.package_name
            _params = _pkg.get_params(columns, merged=True, raw=False)
            if _pkg_name not in tmp_packages:
                tmp_packages[_pkg_name] = _params
                comment = 1
                for _col in columns:
                    widths[_col] = max(widths.get(_col, len(_col)), len(str(_params.get(_col, '')))) + comment
                    comment = 0
        comment = 1
        for _col in columns:
            text += '{}{} '.format(_col, ' ' * (widths[_col] - len(_col) - comment))
            comment = 0
        text = '#{}\n'.format(text.strip())
        for _pkg_name in sorted(tmp_packages, key=lambda x: str(x).lower()):
            _pkg = tmp_packages[_pkg_name]
            line = ''
            for _col in columns:
                line += '{}{} '.format(_pkg[_col], ' ' * (widths[_col] - len(str(_pkg[_col]))))
            text += '{}\n'.format(line.strip())

        Output().write_to_file(text, depslock_file_path)
        self._log.info('Done!')

        return self._root_package.packages
