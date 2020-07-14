# -*- coding: utf-8 -*-
import copy
import fnmatch
import itertools
import logging
import os
import re

from crosspm.helpers.content import DependenciesContent
from crosspm.helpers.exceptions import *
from crosspm.helpers.parser import Parser


class Parser2(Parser):
    def __init__(self, name, data, config):
        super(Parser2, self).__init__(name, data, config)

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
