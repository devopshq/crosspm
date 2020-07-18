# -*- coding: utf-8 -*-
import copy
import json
import os
import time
from collections import OrderedDict
from datetime import datetime

import requests
from artifactory import ArtifactoryPath
from requests.auth import HTTPBasicAuth

from crosspm.adapters.common import BaseAdapter
from crosspm.helpers.exceptions import *  # noqa
from crosspm.helpers.package import Package

CHUNK_SIZE = 1024

setup = {
    "name": [
        "artifactory-aql",
        "jfrog-artifactory-aql",
        "artifactory",
        "jfrog-artifactory",
    ],
}

session = requests.Session()


class Adapter(BaseAdapter):
    def get_packages(self, source, parser, downloader, list_or_file_path, property_validate=True):
        """

        :param source:
        :param parser:
        :param downloader:
        :param list_or_file_path:
        :param property_validate: for `root` packages we need check property, bad if we find packages from `lock` file,
        we can skip validate part
        :return:
        """
        _auth_type = source.args['auth_type'].lower() if 'auth_type' in source.args else 'simple'
        _art_auth_etc = {}
        if 'auth' in source.args:
            self.search_auth(list_or_file_path, source)
            if _auth_type == 'simple':
                _art_auth_etc['auth'] = HTTPBasicAuth(*tuple(source.args['auth']))
                session.auth = _art_auth_etc['auth']
                # elif _auth_type == 'cert':
                #     _art_auth_etc['cert'] = os.path.realpath(os.path.expanduser(source.args['auth']))
        if 'auth' not in _art_auth_etc:
            msg = 'You have to set auth parameter for sources with artifactory-aql adapter'
            # self._log.error(msg)
            raise CrosspmException(
                CROSSPM_ERRORCODE_ADAPTER_ERROR,
                msg
            )

        if 'verify' in source.args:
            _art_auth_etc['verify'] = source.args['verify'].lower in ['true', 'yes', '1']
        else:
            _art_auth_etc['verify'] = False

        _pkg_name_column = self._config.name_column
        _secret_variables = self._config.secret_variables
        _packages_found = OrderedDict()
        _pkg_name_old = ""
        _packed_exist = False
        _packed_cache_params = None
        self._log.info('parser: {}'.format(parser._name))
        for _paths in parser.get_paths(list_or_file_path, source):

            # If "parser"-column specified - find only in this parser
            parser_names = _paths['params'].get('parser')
            if parser_names and parser_names != "*":
                self._log.info("Specified package_parsers: {}".format(parser_names))
                parsers = parser_names.split(',')
                if parser._name not in parsers:
                    self._log.info("Skip parser: {}".format(parser._name))
                    continue

            _packages = []
            _params_found = {}
            _params_found_raw = {}
            last_error = ''
            _pkg_name = _paths['params'][_pkg_name_column]
            if _pkg_name != _pkg_name_old:
                _pkg_name_old = _pkg_name
                self._log.info(
                    '{}: {}'.format(_pkg_name,
                                    {k: v for k, v in _paths['params'].items() if
                                     (k not in (_pkg_name_column, 'repo') and k not in _secret_variables)
                                     }
                                    )
                )
            for _sub_paths in _paths['paths']:
                _tmp_params = dict(_paths['params'])
                self._log.info('repo: {}'.format(_sub_paths['repo']))
                for _path in _sub_paths['paths']:
                    _tmp_params['repo'] = _sub_paths['repo']
                    # ------ START ----
                    # HACK for prefer-local
                    if self._config.prefer_local and not parser.has_rule('properties'):
                        params = parser.get_params_with_extra('path', _paths['params'])
                        for param in params:
                            param['repo'] = _tmp_params['repo']
                            _path_packed = downloader.cache.path_packed(None, param)
                            _packed_exist = os.path.isfile(_path_packed)
                            if _packed_exist:
                                self._log.info("Skip searching, use package cache in path {}".format(_path_packed))
                                _packed_cache_params = param
                                break  # break check local cache
                    if _packed_exist:
                        break  # break connect to artifactory
                        # ------ END  ----
                    _path_fixed, _path_pattern, _file_name_pattern = parser.split_fixed_pattern_with_file_name(_path)
                    try:
                        _artifactory_server = _tmp_params['server']
                        _search_repo = _tmp_params['repo']

                        # Get AQL path pattern, with fixed part path, without artifactory url and repository name
                        _aql_path_pattern = _path_fixed[len(_artifactory_server) + 1 + len(_search_repo) + 1:]
                        if _path_pattern:
                            _aql_path_pattern = _aql_path_pattern + "/" + _path_pattern

                        _aql_query_url = '{}/api/search/aql'.format(_artifactory_server)
                        _aql_query_dict = {
                            "repo": {
                                "$eq": _search_repo,
                            },
                            "path": {
                                "$match": _aql_path_pattern,
                            },
                            "name": {
                                "$match": _file_name_pattern,
                            },
                        }
                        # Remove path if is empty string
                        if not _aql_path_pattern:
                            _aql_query_dict.pop('path')
                        query = 'items.find({query_dict}).include("*", "property")'.format(
                            query_dict=json.dumps(_aql_query_dict))
                        session.auth = _art_auth_etc['auth']
                        r = session.post(_aql_query_url, data=query, verify=_art_auth_etc['verify'])
                        r.raise_for_status()

                        _found_paths = r.json()
                        for _found in _found_paths['results']:
                            _repo_path = "{artifactory}/{repo}/{path}/{file_name}".format(
                                artifactory=_artifactory_server,
                                repo=_found['repo'],
                                path=_found['path'],
                                file_name=_found['name'])
                            _repo_path = ArtifactoryPath(_repo_path, **_art_auth_etc)

                            _mark = 'found'
                            _matched, _params, _params_raw = parser.validate_path(str(_repo_path), _tmp_params)
                            if _matched:
                                _params_found[_repo_path] = {k: v for k, v in _params.items()}
                                _params_found_raw[_repo_path] = {k: v for k, v in _params_raw.items()}
                                _mark = 'match'

                                # Check if it's `root` packages or from `lock` file
                                # ALSO, if from `lock` and have * in name - validate with property
                                property_validate_tmp = property_validate or '*' in _file_name_pattern
                                # If have not rule in config, skip this part
                                if parser.has_rule('properties') and property_validate_tmp:
                                    _found_properties = {x['key']: x.get('value', '') for x in _found['properties']}
                                    _valid, _params = parser.validate(_found_properties, 'properties', _tmp_params,
                                                                      return_params=True)
                                else:
                                    _valid, _params = True, {}
                                if _valid:
                                    _mark = 'valid'
                                    _packages += [_repo_path]
                                    _params_found[_repo_path].update({k: v for k, v in _params.items()})
                                    _params_found[_repo_path]['filename'] = str(_repo_path.name)
                                    _params_found[_repo_path]['parser'] = parser._name
                            self._log.debug('  {}: {}'.format(_mark, str(_repo_path)))
                    except RuntimeError as e:
                        try:
                            err = json.loads(e.args[0])
                        except Exception:
                            err = {}
                        if isinstance(err, dict):
                            # Check errors
                            # :e.args[0]: {
                            #                 "errors" : [ {
                            #                     "status" : 404,
                            #                     "message" : "Not Found"
                            #                  } ]
                            #             }
                            for error in err.get('errors', []):
                                err_status = error.get('status', -1)
                                err_msg = error.get('message', '')
                                if err_status == 401:
                                    msg = 'Authentication error[{}]{}'.format(err_status,
                                                                              (': {}'.format(
                                                                                  err_msg)) if err_msg else '')
                                elif err_status == 404:
                                    msg = last_error
                                else:
                                    msg = 'Error[{}]{}'.format(err_status,
                                                               (': {}'.format(err_msg)) if err_msg else '')
                                if last_error != msg:
                                    self._log.error(msg)
                                last_error = msg

            _package = None

            # HACK for prefer-local
            if _packed_exist:
                # HACK - Normalize params for cached archive
                for key, value in _packed_cache_params.items():
                    if isinstance(value, list):
                        value = ['' if x is None else x for x in value]
                        _packed_cache_params[key] = value
                _package = Package(_pkg_name, None, _paths['params'], downloader, self, parser,
                                   _packed_cache_params, list_or_file_path['raw'], {}, in_cache=True)
            # END HACK
            if _packages:
                _tmp = copy.deepcopy(_params_found)
                _packages = parser.filter_one(_packages, _paths['params'], _tmp)
                if isinstance(_packages, dict):
                    _packages = [_packages]

                if len(_packages) == 1:
                    _stat_pkg = self.pkg_stat(_packages[0]['path'])

                    _params_raw = _params_found_raw.get(_packages[0]['path'], {})
                    _params_tmp = _params_found.get(_packages[0]['path'], {})
                    _params_tmp.update({k: v for k, v in _packages[0]['params'].items() if k not in _params_tmp})
                    _package = Package(_pkg_name, _packages[0]['path'], _paths['params'], downloader, self, parser,
                                       _params_tmp, _params_raw, _stat_pkg)
                    _mark = 'chosen'
                    self._log.info('  {}: {}'.format(_mark, str(_packages[0]['path'])))

                elif len(_packages) > 1:
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

            if (_package is not None) or (not self._config.no_fails):
                _added, _package = downloader.add_package(_pkg_name, _package)
            else:
                _added = False
            if _package is not None:
                _pkg_name = _package.name
            if _added or (_package is not None):
                if (_package is not None) or (not self._config.no_fails):
                    if (_package is not None) or (_packages_found.get(_pkg_name, None) is None):
                        _packages_found[_pkg_name] = _package

            if _added and (_package is not None):
                if downloader.do_load:
                    _package.download()
                    _deps_file = _package.get_file(self._config.deps_lock_file_name)
                    if downloader.recursive:
                        if _deps_file:
                            _package.find_dependencies(_deps_file, property_validate=False)
                        elif self._config.deps_file_name:
                            _deps_file = _package.get_file(self._config.deps_file_name)
                            if _deps_file and os.path.isfile(_deps_file):
                                _package.find_dependencies(_deps_file, property_validate=False)

        # HACK for not found packages
        _package_names = [x[self._config.name_column] for x in list_or_file_path['raw']]
        _packages_found_names = [x.name for x in _packages_found.values()]
        for package in _package_names:
            if package not in _packages_found_names:
                _packages_found[package] = None

        return _packages_found

    def search_auth(self, list_or_file_path, source):
        """
        Looking for auth in env, cmdline, str
        :param list_or_file_path:
        :param source:
        """
        _auth = source.args['auth']
        if isinstance(_auth, str):
            if ':' in _auth:
                _auth = _auth.split(':')
            elif _auth.endswith('}') and (
                    _auth.startswith('{') or ':' in _auth):  # {auth}, {user}:{password}, user:{password}
                _auth = self.get_auth(list_or_file_path, _auth)
                _auth = self.split_auth(_auth)

        if isinstance(_auth, list):
            for i in range(len(_auth)):
                if _auth[i].endswith('}') and (
                        _auth[i].startswith('{') or ':' in _auth[i]):  # {auth}, {user}:{password}, user:{password}
                    _auth[i] = self.get_auth(list_or_file_path, _auth[i])
                    if ':' in _auth[i]:
                        _auth = self.split_auth(_auth[i])

        source.args['auth'] = _auth

    def get_auth(self, list_or_file_path, _auth):
        try:
            return list_or_file_path['raw'][0][_auth[1:-1]]
        except Exception:
            msg = 'Cred {_auth} not found in options'.format(**locals())
            raise CrosspmException(CROSSPM_ERRORCODE_ADAPTER_ERROR, msg)

    def split_auth(self, _auth):
        if ':' in _auth:
            return _auth.split(':')
        else:
            msg = 'Wrong format of oneline credentials. Use user:password'
            raise CrosspmException(CROSSPM_ERRORCODE_ADAPTER_ERROR, msg)

    @staticmethod
    def pkg_stat(package):
        _stat_attr = {'ctime': 'st_atime',
                      'mtime': 'st_mtime',
                      'size': 'st_size'}
        _stat_pkg = package.stat()
        _stat_pkg = {k: getattr(_stat_pkg, k, None) for k in _stat_attr.keys()}
        _stat_pkg = {
            k: time.mktime(v.timetuple()) + float(v.microsecond) / 1000000.0 if isinstance(v, datetime) else v
            for k, v in _stat_pkg.items()
        }
        return _stat_pkg

    def get_usedby(self, source, parser, downloader, list_or_file_path, property_validate=True):
        """

        :param source:
        :param parser:
        :param downloader:
        :param list_or_file_path:
        :param property_validate: for `root` packages we need check property, bad if we find packages from `lock` file,
        we can skip validate part
        :return:
        """
        _auth_type = source.args['auth_type'].lower() if 'auth_type' in source.args else 'simple'
        _art_auth_etc = {}
        if 'auth' in source.args:
            self.search_auth(list_or_file_path, source)
            if _auth_type == 'simple':
                _art_auth_etc['auth'] = HTTPBasicAuth(*tuple(source.args['auth']))
                session.auth = _art_auth_etc['auth']
                # elif _auth_type == 'cert':
                #     _art_auth_etc['cert'] = os.path.realpath(os.path.expanduser(source.args['auth']))
        if 'auth' not in _art_auth_etc:
            msg = 'You have to set auth parameter for sources with artifactory-aql adapter'
            # self._log.error(msg)
            raise CrosspmException(
                CROSSPM_ERRORCODE_ADAPTER_ERROR,
                msg
            )

        if 'verify' in source.args:
            _art_auth_etc['verify'] = source.args['verify'].lower in ['true', 'yes', '1']
        else:
            _art_auth_etc['verify'] = False

        _secret_variables = self._config.secret_variables
        _pkg_name_col = self._config.name_column
        _packages_found = OrderedDict()
        _pkg_name_old = ""

        for _paths in parser.get_paths(list_or_file_path, source):
            _packages = []
            _params_found = {}
            _params_found_raw = {}
            last_error = ''
            _pkg_name = _paths['params'][_pkg_name_col]
            if _pkg_name != _pkg_name_old:
                _pkg_name_old = _pkg_name
                self._log.info(
                    '{}: {}'.format(_pkg_name,
                                    {k: v for k, v in _paths['params'].items() if
                                     (k not in (_pkg_name_col, 'repo') and k not in _secret_variables)
                                     }
                                    )
                )
            for _sub_paths in _paths['paths']:
                _tmp_params = dict(_paths['params'])
                self._log.info('repo: {}'.format(_sub_paths['repo']))
                _tmp_params['repo'] = _sub_paths['repo']
                try:
                    _artifactory_server = _tmp_params['server']
                    _search_repo = _tmp_params['repo']

                    # TODO: Попробовать использовать lru_cache для кеширования кучи запросов
                    _aql_query_url = '{}/api/search/aql'.format(_artifactory_server)
                    _aql_query_dict = {
                        "repo": {
                            "$eq": _search_repo,
                        },
                    }
                    _usedby_aql = parser.get_usedby_aql(_tmp_params)
                    if _usedby_aql is None:
                        continue
                    _aql_query_dict.update(_usedby_aql)
                    query = 'items.find({query_dict}).include("*", "property")'.format(
                        query_dict=json.dumps(_aql_query_dict))
                    session.auth = _art_auth_etc['auth']
                    r = session.post(_aql_query_url, data=query, verify=_art_auth_etc['verify'])
                    r.raise_for_status()

                    _found_paths = r.json()
                    for _found in _found_paths['results']:
                        _repo_path = "{artifactory}/{repo}/{path}/{file_name}".format(
                            artifactory=_artifactory_server,
                            repo=_found['repo'],
                            path=_found['path'],
                            file_name=_found['name'])
                        _repo_path = ArtifactoryPath(_repo_path, **_art_auth_etc)
                        _found_properties = {x['key']: x.get('value', '') for x in _found['properties']}

                        _matched, _params, _params_raw = parser.validate_path(str(_repo_path), _tmp_params)
                        _params_found[_repo_path] = {k: v for k, v in _params.items()}
                        _params_found_raw[_repo_path] = {k: v for k, v in _params_raw.items()}
                        _params = _tmp_params
                        _packages += [_repo_path]
                        _params_found[_repo_path].update({k: v for k, v in _params.items()})
                        _params_found[_repo_path]['filename'] = str(_repo_path.name)

                        _params_raw = _params_found_raw.get(_repo_path, {})
                        params_found = {}

                        # TODO: Проставление params брать из config.yaml usedby
                        params = parser.get_params_from_properties(_found_properties)
                        params.update(parser.get_params_from_path(str(_repo_path)))
                        _package = Package(params[_pkg_name_col], _repo_path, params, downloader, self,
                                           parser,
                                           params_found, _params_raw)

                        _package.find_usedby(None, property_validate=False)
                        _packages_found[str(_repo_path)] = _package
                        # _package.find_dependencies(_deps_file, property_validate=False)
                        _mark = 'chosen'
                        self._log.info('  {}: {}'.format(_mark, str(_repo_path)))
                except RuntimeError as e:
                    try:
                        err = json.loads(e.args[0])
                    except Exception:
                        err = {}
                    if isinstance(err, dict):
                        # Check errors
                        # :e.args[0]: {
                        #                 "errors" : [ {
                        #                     "status" : 404,
                        #                     "message" : "Not Found"
                        #                  } ]
                        #             }
                        for error in err.get('errors', []):
                            err_status = error.get('status', -1)
                            err_msg = error.get('message', '')
                            if err_status == 401:
                                msg = 'Authentication error[{}]{}'.format(err_status,
                                                                          (': {}'.format(
                                                                              err_msg)) if err_msg else '')
                            elif err_status == 404:
                                msg = last_error
                            else:
                                msg = 'Error[{}]{}'.format(err_status,
                                                           (': {}'.format(err_msg)) if err_msg else '')
                            if last_error != msg:
                                self._log.error(msg)
                            last_error = msg

        return _packages_found

    def download_package(self, package, dest_path):
        self.prepare_dirs(dest_path)

        try:
            _stat_pkg = self.pkg_stat(package)
            # with package.open() as _src:
            session.auth = package.auth
            _src = session.get(str(package), verify=package.verify, stream=True)
            _src.raise_for_status()

            with open(dest_path, 'wb+') as _dest:
                for chunk in _src.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        _dest.write(chunk)
                        _dest.flush()

            _src.close()
            os.utime(dest_path, (_stat_pkg['ctime'], _stat_pkg['mtime']))

        except Exception as e:
            code = CROSSPM_ERRORCODE_SERVER_CONNECT_ERROR
            msg = 'FAILED to download package {} at url: [{}]'.format(
                package.name,
                str(package),
            )
            raise CrosspmException(code, msg) from e

        return dest_path

    def prepare_dirs(self, dest_path):
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        elif os.path.exists(dest_path):
            os.remove(dest_path)

    @staticmethod
    def get_package_filename(package):
        if isinstance(package, ArtifactoryPath):
            return package.name
        return ''

    @staticmethod
    def get_package_path(package):
        if isinstance(package, ArtifactoryPath):
            return str(package)
        return ''
