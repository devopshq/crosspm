# -*- coding: utf-8 -*-
import fnmatch
import re
from pathlib import PurePath

from contracts.package_version import PackageVersion
from crosspm.helpers.parser import Parser
from package_parsers.tad_package_name_parser import TadPackageNameParser


class Parser2(Parser):
    def __init__(self, name, data, config):
        super(Parser2, self).__init__(name, data, config)

    def validate_path(self, path, params):
        p = PurePath(path)
        tp = TadPackageNameParser.parse_from_package_name(p.name)
        pv = PackageVersion(tp.version)

        res_params = {}
        res_params.update(params)
        res_params['version'] = pv.release

        res_params_raw = {}
        res_params_raw['version'] = tp.version

        return True, res_params, res_params_raw





    #     return True, params, params

    #params
    # "{'package': 'db', 'version': ['*', None, None], 'server': 'http://127.0.0.1:8081/artifactory', 'repo': 'crosspm'}"
    #result_params
    # {'server': 'http://127.0.0.1:8081/artifactory', 'repo': 'crosspm', 'package': 'db', 'version': [2, '', '']}
    #result_params_raw
    # {'version': '2'}


    def validate_glob_pattern_match(self, _new_path, _path, _res, _sym):
        if '/**/' == _sym:
            re_str = '(.*)\/'
        else:
            re_str = fnmatch.translate(_sym)
        # \/pool\/.*\/\Z(?ms) => \/pool\/.*\/
        if re_str.endswith('\\Z(?ms)'):
            re_str = re_str[:-7]
        found_str = re.match(re_str, _path).group()
        _path = _path[len(found_str):]
        _new_path += found_str
        _res = True
        return _new_path, _path, _res
