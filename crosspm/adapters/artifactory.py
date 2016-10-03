# -*- coding: utf-8 -*-
from crosspm.adapters.common import BaseAdapter
from artifactory import ArtifactoryPath
from crosspm.helpers.exceptions import *
from crosspm.helpers.package import Package
import os
import requests

CHUNK_SIZE = 1024

setup = {
    "name": [
        "artifactory",
        "jfrog-artifactory",
    ],
}


class Adapter(BaseAdapter):
    def get_packages(self, source, parser, downloader, list_or_file_path):
        _auth_type = source.args['auth_type'].lower() if 'auth_type' in source.args else 'simple'
        _art_auth = {}
        if 'auth' in source.args:
            if _auth_type == 'simple':
                _art_auth['auth'] = tuple(source.args['auth'])
            elif _auth_type == 'cert':
                _art_auth['cert'] = os.path.realpath(source.args['auth'])
        if 'verify' in source.args:
            _art_auth['verify'] = source.args['verify'].lower in ['true', 'yes', '1']

        _pkg_name_col = self._config.name_column
        _packages_found = {}
        _pkg_name_old = ""
        for _paths in parser.get_paths(list_or_file_path, source):
            _packages = []
            _pkg_name = _paths['params'][_pkg_name_col]
            if _pkg_name != _pkg_name_old:
                _pkg_name_old = _pkg_name
                print_stdout('{}: {}'.format(_pkg_name, {k: v for k, v in _paths['params'].items() if k != _pkg_name_col}))
            for _path in _paths['paths']:
                _path_fixed, _path_pattern = parser.split_fixed_pattern(_path)
                _repo_paths = ArtifactoryPath(_path_fixed, **_art_auth)
                for _repo_path in _repo_paths.glob(_path_pattern):
                    _mark = 'found'
                    if parser.validate_path(str(_repo_path), _paths['params']):
                        _mark = 'match'
                        if parser.validate(_repo_path.properties, 'properties', _paths['params']):
                            _mark = 'valid'
                            _packages += [_repo_path]
                    print_stdout('  {}: {}'.format(_mark, str(_repo_path)))
            _package = None
            if _packages:
                _packages = parser.filter_one(_packages, _paths['params'])
                if type(_packages) is dict:
                    _packages = [_packages]

                if len(_packages) == 1:
                    # one package found: ok!
                    _package = Package(_pkg_name, _packages[0]['path'], _paths['params'], downloader, self, parser, _packages[0]['params'])
                    _mark = 'chosen'
                    print_stdout('  {}: {}'.format(_mark, str(_packages[0]['path'])))

                elif len(_packages) > 1:
                    # TODO: multiple packages found: wtf?!
                    raise CrosspmException(
                        CROSSPM_ERRORCODE_MULTIPLE_DEPS,
                        'Multiple instances found for package [{}] not found.'.format(_pkg_name)
                    )
                else:
                    # Package not found: may be error, but it could be in other source.
                    pass
            else:
                # Package not found: may be error, but it could be in other source.
                pass
                # _pkg_name = self._config.get_column_name(0)
                # raise CrosspmException(
                #     CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
                #     'Package [{}] not found.'.format(_pkg_name)
                # )
            _added, _package = downloader.add_package(_pkg_name, _package)
            if _added or _package is not None:
                _packages_found[_pkg_name] = _package

            if _added and _package is not None:
                if downloader.do_load:
                    _package.download(downloader.packed_path)

                    _deps_file = _package.get_file(self._config.deps_lock_file_name, downloader.temp_path)

                    if _deps_file:
                        _package.find_dependencies(_deps_file)

        return _packages_found

    def download_package(self, package, dest_path):
        _dest_file = os.path.join(dest_path, package.name)

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        elif os.path.exists(_dest_file):
            # TODO: Check if we can keep existing file
            os.remove(_dest_file)

        try:
            #with package.open() as _src:
            _src = requests.get(str(package), auth=package.auth, verify=package.verify, stream=True)
            _src.raise_for_status()

            with open(_dest_file, 'wb+') as _dest:
                for chunk in _src.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        _dest.write(chunk)
                        _dest.flush()

            _src.close()

        except Exception as e:
            code = CROSSPM_ERRORCODE_SERVER_CONNECT_ERROR
            msg = 'FAILED to download package {} at url: [{}]'.format(
                package.name,
                str(package),
            )
            raise CrosspmException(code, msg) from e

        return _dest_file
