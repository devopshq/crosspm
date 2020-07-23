# -*- coding: utf-8 -*-
import fnmatch
import re
from pathlib import PurePath

from addict import Dict

from contracts.package_version import PackageVersion
from crosspm.helpers.parser import Parser
from package_parsers.debian_package_name_parser import DebianPackageNameParser


class Parser2(Parser):
    def __init__(self, name, data, config):
        # pass
        super().__init__(name, data, config)

    def get_vars(self):
        return ['server', 'repo', 'package', 'version']

    def validate_path(self, path, params):
        p = PurePath(path)
        debian_package = DebianPackageNameParser.parse_from_package_name(p.name)
        package_version = PackageVersion(debian_package.version)

        res_params = Dict()
        res_params.update(params)
        res_params.version = package_version.release

        res_params_raw = Dict()
        res_params_raw.version = debian_package.version

        return True, res_params, res_params_raw

    def merge_with_mask(self, column, value):
        return value

