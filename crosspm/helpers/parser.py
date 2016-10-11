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
    _rules_vars_extra = {}
    _columns = {}
    _col_types = []
    _sort = []
    _index = -1


    def __init__(self, name, data, config):
        self._name = name
        self._sort = data.pop('sort', self._sort)
        self._index = data.pop('index', self._index)
        self._rules = {k: v for k, v in data.items() if k not in ['columns']}
        if 'columns' in data:
            self._columns = {k: self.parse_value_template(v) for k, v in data['columns'].items() if v != ''}
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
            self._rules_vars_extra[_name] = {}
            for i, _item in enumerate(self._rules_vars[_name]):
                _tmp = [x for x in _item.split('|') if x]
                if len(_tmp) > 1:
                    self._rules[_name] = self._rules[_name].replace(('{%s}' % _item), ('{%s}' % _tmp[0]))
                    self._rules_vars[_name][i] = _tmp[0]
                    self._rules_vars_extra[_name][_tmp[0]] = _tmp[1:]

    def parse_by_mask(self, column, value, types=False, extMask=False):
        if column not in self._columns:
            return value  # nothing to parse
        _res = []
        # extMask = extMask and value == '*'
        orig_value = value
        rule_parsed = self._columns[column]
        prev_om_sep = False
        om_sep = ''
        for _part in rule_parsed:
            if _part[1]:
                for _subpart in _part[0]:
                    if not _subpart[1]:
                        om_sep = _subpart[0]
                        break
        # TODO: make parsing smarter
        for x, _part in enumerate(rule_parsed):
            for y, _subpart in enumerate(_part[0]):
                if _subpart[1]:
                    _pos = -1
                    _sym = ''
                    if y < len(_part[0]) - 1:
                        _sym = _part[0][y + 1][0]
                        _pos = value.find(_sym)
                        cur_om_sep = _pos >= 0 and _part[1]
                    else:
                        cur_om_sep = False
                        z = x
                        while True:
                            if z < len(rule_parsed) - 1:
                                z += 1
                                _sym = rule_parsed[z][0][0][0]
                                _pos = value.find(_sym)
                                if _pos >= 0:
                                    cur_om_sep = rule_parsed[z][1]
                                    break
                                elif not rule_parsed[z][1]:
                                    break
                            else:
                                break

                    if _pos >= 0:
                        _atom = value[:_pos]
                        value = value[_pos + len(_sym):]
                    else:
                        if extMask:
                            if orig_value == '*':
                                _atom = '*' if not _part[1] else None
                            elif _part[1]:
                                if prev_om_sep:
                                    _atom = value  # '2.3.*-*' - Do not include versions without last part
                                    # _atom = ''   # '2.3.*-'  - Do not include versions with last part
                                else:
                                    _atom = None  # '2.3.*'   - Include versions both with or without last part
                            else:
                                if om_sep:
                                    _pos = value.find(om_sep)
                                    if _pos >= 0:
                                        _atom = value[:_pos]
                                        if _atom != '*':
                                            value = value[_pos:]
                                    else:
                                        _atom = value
                                        if _atom != '*':
                                            value = ''
                                else:
                                    _atom = value
                                    if _atom != '*':
                                        value = ''
                        else:
                            _atom = value
                            value = ''

                    if types:
                        _res += [(_atom, _subpart[0])]
                    else:
                        _res += [_atom]
                    prev_om_sep = cur_om_sep

        return _res

    def merge_with_mask(self, column, value):
        if column not in self._columns:
            if type(value) in [list, tuple]:
                value = ''.join(value)
            return value  # nothing to parse
        if type(value) not in [list, tuple]:
            return value  # nothing to parse
        _res = ''
        _res_tmp = ''
        rule_parsed = self._columns[column]
        _value = value
        for _part in rule_parsed:
            for _subpart in _part[0]:
                if _subpart[1]:
                    _exist = False
                    if len(_value) > 0:
                        if not _part[1]:
                            _exist = True
                        elif _value[0] not in ('', None):
                            _exist = True
                    if _exist:
                        _res_atom = str(_value[0])
                        if _part[1]:
                            if _res_atom in [None, '*', '']:
                                _res_tmp = ''
                                if _res and _res[-1] == '*':
                                    _res_atom = ''
                            _res += _res_tmp
                            _res_tmp = ''
                        _res += _res_atom
                        _value = _value[1:]
                    else:
                        _res_tmp = ''
                        if _part[1]:
                            break
                        else:
                            # TODO: Error handling?
                            break

                else:
                    if _part[1]:
                        _res_tmp += _subpart[0]
                    else:
                        _res_tmp = ''
                        _res += _subpart[0]

        return _res + _res_tmp

    def validate_by_mask(self, column, value, param):
        if column not in self._columns:
            _res = True  # nothing to validate
        elif type(param) not in [list, tuple]:
            _res = False
        else:
            _res = True
            for i, (_tmp, tp) in enumerate(self.parse_by_mask(column, value, True)):
                if tp == 'int':
                    try:
                        _tmp = int(_tmp)
                    except:
                        _tmp = str(_tmp)
                if not self.validate_atom(_tmp, param[i]):
                    _res = False
                    break

        return _res

    @staticmethod
    def validate_atom(value, text):
        _sign = ''
        if text:
            if text.startswith(('>=', '<=', '==',)):
                _sign = text[:2]
                text = text[2:]
            elif text.startswith(('>', '<', '=',)):
                _sign = text[:1]
                text = text[1:]
                if _sign == '=':
                    _sign = '=='

        var1 = value
        var2 = text if text else '*'
        if type(var1) is int:
            try:
                var2 = int(var2)
                if not _sign:
                    _sign = '=='
            except:
                var1 = str(var1)

        if _sign:
            _match = eval('var1 {} var2'.format(_sign))
        else:
            _match = fnmatch.fnmatch(var1, var2)

        return _match

    def validate_path(self, path, params):
        _rule_name = 'path'
        _path = str(path)
        _new_path = ''

        def get_atom(_x, _y, _path0):
            _pos = -1
            if _y < len(_part[0]) - 1:
                _sym0 = _part[0][_y + 1][0]
                _pos = _path0.find(_sym0)
            elif _x < len(rule_parsed) - 1:
                if rule_parsed[_x + 1][1]:
                    _tmp0 = [xx.strip() for xx in rule_parsed[_x + 1][0][0][0].split('|')]
                else:
                    _tmp0 = [rule_parsed[_x + 1][0][0][0]]
                for _sym0 in _tmp0:
                    _pos = _path0.find(_sym0)
                    if _pos >= 0:
                        break

            if _pos >= 0:
                _atom0 = _path0[:_pos]
                _path0 = _path0[_pos:]
            else:
                _atom0 = _path0
                _path0 = ''
            return _atom0, _path0

        def iter_with_extras(_col_name, _value0):
            _res0 = [_value0]
            if _col_name in self._rules_vars_extra[_rule_name]:
                _res0 += self._rules_vars_extra[_rule_name][_col_name]
            for _res1 in _res0:
                yield _res1

        _res = True
        rule = self._rules[_rule_name]
        rule_parsed = self.parse_value_template(rule)
        for x, _part in enumerate(rule_parsed):
            for y, _subpart in enumerate(_part[0]):
                if _subpart[1]:
                    _value = params[_subpart[0]]
                    if _subpart[0] in self._columns:
                        # we have a mask to process
                        _atom, _path = get_atom(x, y, _path)
                        _match = False
                        for _value_item in iter_with_extras(_subpart[0], _value):
                            if self.validate_by_mask(_subpart[0], _atom, _value_item):
                                _new_path += _atom
                                _match = True
                                break
                        if not _match:
                            return False
                    else:
                        # it's a plain value
                        _plain = any(x in _value for x in ('>=', '<=', '==', '>', '<', '=', '*'))
                        if _plain:
                            # _atom = _path[:len(_value)]
                            # _rule = _part.format(**params)
                            _match = False
                            for _value_item in iter_with_extras(_subpart[0], _value):
                                _atom = _path[:len(_value_item)]
                                if fnmatch.fnmatch(_atom, _value_item):  # may be just comparing would be better
                                    _new_path += _atom
                                    _path = _path[len(_value_item):]
                                    _match = True
                                    break
                            if not _match:
                                return False
                        else:
                            _atom, _path = get_atom(x, y, _path)
                            _match = False
                            for _value_item in iter_with_extras(_subpart[0], _value):
                                if self.validate_atom(_value_item, _atom):
                                    _new_path += _atom
                                    _match = True
                                    break
                            if not _match:
                                return False

                else:
                    # just part of template
                    _res = False
                    if _part[1]:
                        # square brackets means this part can be one of values
                        _tmp = [xx.strip() for xx in _subpart[0].split('|')]
                    else:
                        _tmp = [_subpart[0]]
                    for _sym in _tmp:
                        _atom = _path[:len(_sym)]
                        if fnmatch.fnmatch(_atom, _sym):  # may be just comparing would be better
                            _path = _path[len(_sym):]
                            _new_path += _atom
                            _res = True
                            break

                    if not _res:
                        return False

        return _res

    def validate(self, value, rule_name, params):
        if rule_name not in self._rules:
            return True
            # raise CrosspmException(
            #     CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR,
            #     'Parser rule for [{}] not found in config.'.format(rule_name)
            # )
        if len(self._rules[rule_name]) == 0:
            return True  # len(value) == 0
        if self._rules[rule_name] is None:
            return True
        _res = False
        # _dirty = self._rules[rule_name].format(**params)
        _dirties = self.fill_rule(rule_name, params)
        for _dirty in _dirties:
            # TODO: Use split_with_regexp() instead
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
                                    'Parser rule for [{}] not able to process [{}] data type.'.format(rule_name,
                                                                                                      type(_tmp_val))
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
            if self.values_match(_value, value, _values):
                if type(_values) is dict:
                    _value = _values[_value]
                yield _value

    @staticmethod
    def values_match(_value, value, _values=None):
        if value is None:
            return _value is None
        _sign = ''
        if value.startswith(('>=', '<=', '==',)):
            _sign = value[:2]
            value = value[2:]
        elif value.startswith(('>', '<', '=',)):
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

        if int in [type(var1), type(var2)]:
            try:
                var1a = int(var1)
                var2a = int(var2)
                if not _sign:
                    _sign = '=='
            except:
                var1a = str(var1)
                var2a = str(var2)
            var1, var2 = var1a, var2a

        if _sign:
            _match = eval('var1 {} var2'.format(_sign))
        else:
            _match = fnmatch.fnmatch(var1, var2)

        return _match

    def fill_rule(self, rule_name, params):
        def fill_rule_inner(_cols, _params_inner, _pars=None):
            if _pars is None:
                _pars = {}
            for _cl in _cols:
                for _val in _cl[1]:
                    _pars[_cl[0]] = _val
                    if len(_cols) > 1:
                        _params_inner = fill_rule_inner(_cols[1:], _params_inner, _pars)
                    else:
                        _params_inner.append({k: v for k, v in _pars.items()})
                break
            return _params_inner

        _params = {k: v for k, v in params.items()}
        _res = []
        _columns = []
        for _col, _valued in self._config.iter_valued_columns2(self._rules_vars[rule_name]):
            if _valued:
                _columns += [[_col, [x for x in self.iter_matched_values(_col, params[_col])]]]
            else:
                if type(params[_col]) not in [list, tuple]:
                    _tmp = [params[_col]]
                else:
                    _tmp = [x for x in params[_col]]
                for i, _tmp_item in enumerate(_tmp):
                    if _tmp_item and _tmp_item.startswith(('>=', '<=', '==', '>', '<', '=',)):
                        _tmp[i] = '*'

                _params[_col] = self.merge_with_mask(_col, _tmp)
            if _col in self._rules_vars_extra[rule_name]:
                if len(self._rules_vars_extra[rule_name][_col]) > 0:
                    _params[_col] = '[%s%s]' % (_params[_col], ''.join('|{}'.format(x) for x in self._rules_vars_extra[rule_name][_col]))

        for _par in fill_rule_inner(_columns, []):
            _params.update(_par)
            _res += [self._rules[rule_name].format(**_params)]

        if len(_res) == 0:
            _res = [self._rules[rule_name].format(**_params)]
        return _res

    def get_paths(self, list_or_file_path, source):
        if 'path' not in self._rules:
            return None
        _paths = []
        for _params in self.iter_packages_params(list_or_file_path):
            for _repo in source.args['repo']:
                _params['server'] = source.args['server']
                _params['repo'] = _repo
                # _dirty = self._rules['path'].format(**_params)
                _dirties = self.fill_rule('path', _params)
                # _params.pop('server')
                # _params.pop('repo')
                for _dirty in _dirties:
                    # TODO: Use split_with_regexp() instead
                    _dirty = [x.split(']') for x in _dirty.split('[')]
                    _dirty = self.list_flatter(_dirty)
                    _paths += [{'paths': self.get_variants(_dirty, []),
                                'params': {k: v for k, v in _params.items()},
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

                    if not line or line.startswith(('#', '[',)):
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
            k, v = self._config.check_column_value(i, v, True)
            _vars[k] = self.parse_by_mask(k, v, False, True)

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

    @staticmethod
    def split_with_regexp(regexp, text):
        prev_pos = 0
        _res = []
        for x in ([x.group()[1:-1].strip(), x.span()] for x in re.finditer(regexp, text)):
            if x[1][0] > prev_pos:
                _res += [[text[prev_pos:x[1][0]], False]]
            _res += [[x[0], True]]
            prev_pos = x[1][1]
        if prev_pos < len(text):
            _res += [[text[prev_pos:], False]]
        return _res

    def parse_value_template(self, value):
        # _regexp = ''
        must_not = self.split_with_regexp('\[.*?\]', value)
        for i, x in enumerate(must_not):
            must_not[i] = [self.split_with_regexp('{.*?}', x[0]), x[1]]
            # _atom = '(?P<_1_int>[\\w*><=]+)'
        return must_not

    @staticmethod
    def split_fixed_pattern(path):
        _first_pattern_pos = path.find('*')
        _path_separator_pos = path.rfind('/', 0, _first_pattern_pos) + 1
        _path_fixed = path[:_path_separator_pos]
        _path_pattern = path[_path_separator_pos:]
        return _path_fixed, _path_pattern

    # TODO: optimize code merging duplicated parts
    def filter_one(self, packages, params):

        def get_all_masked_atoms(path):
            def get_atom(_x, _y, _path0):
                _pos = -1
                if _y < len(_part[0]) - 1:
                    _sym0 = _part[0][_y + 1][0]
                    _pos = _path0.find(_sym0)
                elif _x < len(rule_parsed) - 1:
                    if rule_parsed[_x + 1][1]:
                        _tmp0 = [xx.strip() for xx in rule_parsed[_x + 1][0][0][0].split('|')]
                    else:
                        _tmp0 = [rule_parsed[_x + 1][0][0][0]]
                    for _sym0 in _tmp0:
                        _pos = _path0.find(_sym0)
                        if _pos >= 0:
                            break

                if _pos >= 0:
                    _atom0 = _path0[:_pos]
                    _path0 = _path0[_pos:]
                else:
                    _atom0 = _path0
                    _path0 = ''
                return _atom0, _path0

            _path = str(path)
            _atom_list = []
            _atoms_found = {}
            rule = self._rules['path']
            rule_parsed = self.parse_value_template(rule)
            for x, _part in enumerate(rule_parsed):
                for y, _subpart in enumerate(_part[0]):
                    if _subpart[1]:
                        _value = params[_subpart[0]]
                        if _subpart[0] in self._columns:
                            # we have a mask to process
                            if _subpart[0] not in _atoms_found:
                                _atom, _path = get_atom(x, y, _path)
                                _atom = self.parse_by_mask(_subpart[0], _atom, True)
                                _tmp_atom = []
                                for x in _atom:
                                    if x[1] == 'int':
                                        try:
                                            _tmp_atom += [int(x[0])]
                                        except:
                                            _tmp_atom += [x[0]]
                                    else:
                                        _tmp_atom += [x[0]]

                                _atoms_found[_subpart[0]] = _tmp_atom
                        else:
                            # it's a plain value
                            _plain = any(x in _value for x in ('>=', '<=', '==', '>', '<', '=', '*'))
                            if _plain:
                                _path = _path[len(_value):]
                            else:
                                _atom, _path = get_atom(x, y, _path)
                                if _subpart[0] not in _atoms_found:
                                    _atoms_found[_subpart[0]] = [_atom]
                    else:
                        # just part of template
                        if _part[1]:
                            # square brackets means this part can be one of values
                            _tmp = [xx.strip() for xx in _subpart[0].split('|')]
                        else:
                            _tmp = [_subpart[0]]
                        for _sym in _tmp:
                            _atom = _path[:len(_sym)]
                            if fnmatch.fnmatch(_atom, _sym):  # may be just comparing would be better
                                _path = _path[len(_sym):]
                                break

            return _atoms_found

        def filter_fn(item):
            result = True
            _atoms_found = item['params']
            for _atom_name in item['columns']:
                if _atom_name in _atoms_found:
                    _rules = params[_atom_name]
                    if type(_rules) not in [list, tuple]:
                        _rules = [_rules]
                    _vars = _atoms_found[_atom_name]
                    if type(_vars) not in [list, tuple]:
                        _vars = [_vars]
                    i = -1
                    for _column in item['columns'][_atom_name]:
                        for _sub_col in _column[0]:
                            if _sub_col[1]:
                                i += 1
                                if _column[1]:
                                    _var = _vars[i] if len(_vars) > i else ''
                                    _rule = _rules[i] if len(_rules) > i else ''
                                    if _rule is None:         # '2.3.*'   - Include versions both with or without last part
                                        pass
                                    elif _rule == '' and _var and len(
                                            str(_var)) > 0:   # '2.3.*-'  - Do not include versions with last part
                                        result = False
                                        break
                                    elif _rule and not _var:  # '2.3.*-*' - Do not include versions without last part
                                        result = False
                                        break
                        if not result:
                            break
                if not result:
                    break

            return result

        def sorted_fn(item):
            result = []
            _atoms_found = item['params']
            for _atom_name in self._sort:
                if _atom_name == '*':
                    result += [_atoms_found[x] for x in _atoms_found if x not in self._sort]
                else:
                    result += [_atoms_found.get(_atom_name, [])]

            result = [item for sublist in result for item in sublist]

            return result

        ext_packages = [{'params': get_all_masked_atoms(x), 'columns': self._columns, 'path': x} for x in packages]

        # TODO: Filter by columns with parsing template (i.e. version)
        filtered_packages = list(filter(
            filter_fn,
            ext_packages,
        ))

        sorted_packages = sorted(
            filtered_packages,
            key=sorted_fn,
        )

        try:
            result = sorted_packages[self._index]
        except:
            result = []
        return result
