# -*- coding: utf-8 -*-
import re
import fnmatch
import os
from crosspm.helpers.exceptions import *


class Parser(object):
    # _name = ''
    # _rules = {}
    # _config = None
    _rules_vars = {}

    def __init__(self, name, data, config):
        self._name = name
        self._rules = data
        self._config = config
        self.init_rules_vars()

    def get_vars(self):
        _vars = []
        for _rule_vars in self._rules_vars.values():
            _vars += [x for x in _rule_vars if x not in _vars]
        return _vars

    def init_rules_vars(self):
        self._rules_vars = {}
        for _name, _rule in self._rules.items():
            self._rules_vars[_name] = list({x[1:-1].strip(): 0 for x in re.findall('{.*?}', _rule)}.keys())

    def validate(self, value, rule_name, params):
        if rule_name not in self._rules:
            raise CrosspmException(
                CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR,
                'Parser rule for [{}] not found in config.'.format(rule_name)
            )
        if self._rules[rule_name] is None:
            return True
        _res = False
        #_dirty = self._rules[rule_name].format(**params)
        _dirties = self.fill_rule(rule_name, params)
        for _dirty in _dirties:
            _dirty = [x.split(']') for x in _dirty.split('[')]
            _dirty = self.list_flatter(_dirty)
            _variants = self.get_variants(_dirty, [])
            if type(value) is str:
                _res = value in _variants
            elif type(value) in (list, tuple):
                for _variant in _variants:
                    if _variant in value:
                        _res = True
                        break
            elif type(value) is dict:
                for _variant in _variants:
                    _tmp = [x.strip() for x in _variant.split('=')]
                    _tmp = [x if len(x) > 0 else '*' for x in _tmp]
                    for _key in fnmatch.filter(value.keys(), _tmp[0]):
                        if len(_tmp) > 1:
                            _tmp_val = value[_key]
                            if type(_tmp_val) is str:
                                _tmp_val = [_tmp_val]
                            elif type(_tmp_val) not in [list, tuple, dict]:
                                raise CrosspmException(
                                    CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR,
                                    'Parser rule for [{}] not able to process [{}] data type.'.format(rule_name, type(_tmp_val))
                                )
                            if len(fnmatch.filter(_tmp_val, _tmp[1])) > 0:
                                _res = True
                                break
                        else:
                            _res = True
                            break
            else:
                raise CrosspmException(
                    CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR,
                    'Parser rule for [{}] not able to process [{}] data type.'.format(rule_name, type(value))
                )
        return _res

    def iter_matched_values(self, column_name, value):
        _values = self._config.get_values(column_name)
        for _value in _values:
            _sign = ''
            if value.startswith(('>=', '<=', '==', )):
                _sign = value[:2]
                value = value[2:]
            elif value.startswith(('>', '<', '=', )):
                _sign = value[:1]
                value = value[1:]
                if _sign == '=':
                    _sign = '=='

            var1, var2 = _value, value
            if type(_values) is dict:
                var2 = 0 if type(var1) is int else ''
                for k, v in _values.items():
                    if value == v:
                        var2 = k
                        break

            if _sign:
                _match = eval('{} {} {}'.format(var1, _sign, var2))
            else:
                # TODO: implement * (any) sign check
                _match = var1 == var2

            if _match:
                if type(_values) is dict:
                    var1 = _values[var1]
                yield var1

    def fill_rule(self, rule_name, params):
        _params = {k: v for k, v in params.items()}
        _res = []
        for _col in self._config.iter_valued_columns(self._rules_vars[rule_name]):
            for _value in self.iter_matched_values(_col, params[_col]):
                _params[_col] = _value
                _res += [self._rules['path'].format(**_params)]
            _params[_col] = ''
        if len(_res) == 0:
            _res = [self._rules['path'].format(**_params)]
        return _res

    def get_paths(self, list_or_file_path, source):
        if 'path' not in self._rules:
            return None
        _paths = []
        for _params in self.iter_packages_params(list_or_file_path):
            for _repo in source.args['repo']:
                _params['server'] = source.args['server']
                _params['repo'] = _repo
                #_dirty = self._rules['path'].format(**_params)
                _dirties = self.fill_rule('path', _params)
                _params.pop('server')
                _params.pop('repo')
                for _dirty in _dirties:
                    _dirty = [x.split(']') for x in _dirty.split('[')]
                    _dirty = self.list_flatter(_dirty)
                    _paths += [{'paths': self.get_variants(_dirty, []),
                                'params': _params,
                                }]
        return _paths

    def get_variants(self, dirty, paths):
        if len(dirty) == 1:
            paths.append(dirty[0])
        else:
            for i, stub in enumerate(dirty):
                if i % 2 != 0:
                    for _variant in stub.split("|"):
                        _res = ''.join(dirty[:i]) + _variant
                        _res += dirty[i + 1] if len(dirty) > i else ''
                        _res = [_res]
                        if len(dirty) > i + 1:
                            _res += dirty[i + 2:]
                        # print(_res)
                        paths = self.get_variants(_res, paths)
                    break
        return paths

    def iter_packages_params(self, list_or_file_path):
        if type(list_or_file_path) is str:
            if not os.path.exists(list_or_file_path):
                raise CrosspmException(
                    CROSSPM_ERRORCODE_FILE_DEPS_NOT_FOUND,
                    'File not found: [{}]'.format(list_or_file_path),
                )

            with open(list_or_file_path, 'r') as f:
                for i, line in enumerate(f):
                    line = line.strip()

                    if not line or line.startswith(('#', '[', )):
                        continue

                    yield self.get_package_params(i, line)
        else:
            for _item in list_or_file_path:
                yield _item

    def get_package_params(self, line_no, line):
        _vars = {}
        for i, v in enumerate(line.split()):
            v = v.strip()
            if v == '-':
                v = None  # get default value on next line
            _vars.update(self._config.check_column_value(i, v))

        # TODO: version parsing? ex: version = tuple(v.split('.')) or regexp or fnmatch

        if len(_vars) == 0:
            raise CrosspmException(
                CROSSPM_ERRORCODE_WRONG_SYNTAX,
                'Nothing parsed at line {}: [{}]'.format(line_no, line.strip())
            )

        _vars = self._config.complete_params(_vars)

        return _vars

    def list_flatter(self, _src):
        _res = []
        for x in _src:
            _res += self.list_flatter(x) if type(x) in [list, tuple] else [x]
        return _res
