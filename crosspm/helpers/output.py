# -*- coding: utf-8 -*-

import json
import logging
import os
import re
from jinja2 import Environment, FileSystemLoader
from collections import OrderedDict

from crosspm.helpers.exceptions import *
from crosspm.helpers.parser import Parser

_output_format_map = {}  # Contain map for output format, load from decorator

(
    PLAIN,
    DICT,
    LIST
) = range(3)


class OutFormat:
    def __init__(self, value, esc_path=False):
        self._value = value
        self._esc_path = esc_path

    def __format__(self, fmt):
        result = self._value
        fmts = fmt.split('.')
        if self._esc_path and ('path' not in fmts):
            fmts.insert(0, 'path')
        for fmt in fmts:
            if fmt == 'upper':
                result = str(result).upper()
            elif fmt == 'lower':
                result = str(result).lower()
            elif fmt == 'quote':
                result = '"{}"'.format(result)
            elif fmt == 'unquote':
                result = str(result).strip('"')
            elif fmt == 'safe':
                result = str(result).replace('-', '_')
                result = re.sub(r'[^A-Z_a-z_0-9]', '', result)
                if result:
                    if not (result[0].isalpha() or '_' == result[0]):
                        result = '_' + result
            elif fmt == 'path':
                result = str(result).replace('\\\\', '\\').replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

        return str(result)


def register_output_format(name):
    """
    Load output format function to dictionary (decorator with this function name)
    """

    def check_decorator(fn):
        _output_format_map[name] = fn

        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    return check_decorator


class Output:
    _output_config = {
        'root': {'PACKAGES_ROOT'},
        # 'key': 'package',
        'value': 'path',
        # 'columns': [
        #     {
        #         'column': 'package',
        #         'value': '{:upper}_ROOT',
        #     },
        #     {
        #         'column': 'path',
        #         'value': '{}',
        #     }
        # ]
    }
    _name_column = ''
    _columns = []

    def __init__(self, data=None, name_column='', config=None):
        self._log = logging.getLogger('crosspm')
        self._config = config
        if name_column:
            self._name_column = name_column
            self._output_config['key'] = name_column
        if data and isinstance(data, dict):
            self._output_config = data
        # self.init_config()
        if 'columns' not in self._output_config:
            self._output_config['columns'] = []

        if len(self._output_config['columns']) == 0:
            # TODO: implement this:
            # if config.no_fails:
            #     param_list = [x for x in config.get_fails('unique', {})]
            #     if self._name_column not in param_list:
            #         param_list.insert(0, self._name_column)
            #     pkg_name = '/'.join('{%s:upper}' % x for x in param_list)
            # else:
            pkg_name = '{:upper}_ROOT'

            self._output_config['columns'] = [
                {
                    'column': self._name_column,
                    'value': pkg_name,
                },
                {
                    'column': 'path',
                    'value': '{}',
                },
            ]

        self.init_config()
        if 'columns' not in self._output_config:
            self._output_config['columns'] = []

    def init_config(self):
        root = self._output_config.get('root', '')
        if isinstance(root, str):
            self._output_config['type'] = PLAIN
        elif isinstance(root, (dict, set)):
            self._output_config['type'] = DICT
            root = [x for x in root]
            self._output_config['root'] = root[0] if len(root) > 0 else ''
        elif isinstance(root, (list, tuple)):
            self._output_config['type'] = LIST
            self._output_config['root'] = root[0] if len(root) > 0 else ''

        key = self._output_config.get('key', '')
        key0 = None

        if 'columns' in self._output_config:
            self._columns = []
            for item in self._output_config['columns']:
                if not item.get('value', ''):
                    item['value'] = '{}'
                if not item.get('name', ''):
                    item['name'] = '{}'
                if not item.get('column', ''):
                    item['column'] = ''
                    for cl in [y for y in [x[0] for x in Parser.split_with_regexp('{.*?}', item['name']) if x[1]] if y]:
                        col = cl.split(':')[0]
                        if col:
                            item['column'] = col
                            break
                if item['column']:
                    self._columns.append(item['column'])
                    if key == item['column']:
                        key0 = ''
                    elif key0 is None:
                        key0 = item['column']

        if key0:
            key = key0
        self._output_config['key'] = key

        if self._columns:
            if self._name_column and self._name_column not in self._columns:
                self._columns.append(self._name_column)
        else:
            if not self._name_column:
                self._name_column = 'package'
        if 'value' not in self._output_config:
            self._output_config['value'] = ''

    @staticmethod
    def get_var_name(pkg_name):
        result = '{:upper.safe}'.format(OutFormat(pkg_name))
        return result

    def write_to_file(self, text, out_file_path):
        out_dir_path = os.path.dirname(out_file_path)

        if not os.path.exists(out_dir_path):
            self._log.info('mkdirs [%s] ...', out_dir_path)
            os.makedirs(out_dir_path)

        elif not os.path.isdir(out_dir_path):
            raise CrosspmException(
                CROSSPM_ERRORCODE_FILE_IO,
                'Unable to make directory [{}]. File with the same name exists'.format(
                    out_dir_path
                ))

        with open(out_file_path, 'w+') as f:
            f.write(text)

    @staticmethod
    def get_output_types():
        return list(_output_format_map.keys())

    def write_output(self, params, packages):
        """
        Функция вызывает определенную функцию для фиксированного out-format
        :param params:
        :param packages:
        :return:
        """
        if params['out_format'] not in _output_format_map:
            raise CrosspmException(
                CROSSPM_ERRORCODE_UNKNOWN_OUT_TYPE,
                'Unknown out_format: [{}]'.format(params['out_format']),
            )

        f = _output_format_map[params['out_format']]
        result = f(self, packages, **params)

        if result:
            out_file_path = os.path.realpath(os.path.expanduser(params['output']))
            self.write_to_file(result, out_file_path)
            self._log.info(
                'Write packages info to file [%s]\ncontent:\n\n%s',
                out_file_path,
                result,
            )

    def format_column(self, column, name, value):
        for item in self._output_config['columns']:
            if item['column'] == column:
                name = item['name'].format(OutFormat(name))
                value = item['value'].format(OutFormat(value))
                break
        return {'name': name, 'value': value}

    @register_output_format('stdout')
    def output_format_stdout(self, packages, **kwargs):
        self._output_config['type'] = PLAIN
        _packages = self.output_format_module(packages)
        for k in _packages:
            v = _packages[k]
            sys.stdout.write('{}: {}\n'.format(self.get_var_name(k), v))
            sys.stdout.flush()
        return None

    @register_output_format('shell')
    def output_format_shell(self, packages, **kwargs):
        self._output_config['type'] = PLAIN
        result = '\n'
        _packages = self.output_format_module(packages)
        for k in _packages:
            v = _packages[k]
            result += "{}='{}'\n".format(self.get_var_name(k), v)
        result += '\n'
        return result

    @register_output_format('jinja')
    def output_format_jinja(self, packages, output_template, **kwargs):
        output_template = os.path.realpath(output_template)
        template_dir, template_name = os.path.split(output_template)
        j2_env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True)
        result = j2_env.get_template(template_name).render(packages=packages)
        return result

    @register_output_format('cmd')
    def output_format_cmd(self, packages, **kwargs):
        self._output_config['type'] = PLAIN
        result = '\n'
        _packages = self.output_format_module(packages)
        for k in _packages:
            v = _packages[k]
            result += "set {}={}\n".format(self.get_var_name(k), v)
        result += '\n'
        return result

    @register_output_format('lock')
    def output_format_lock(self, packages, **kwargs):
        """ Text to lock file """
        self._output_config['type'] = PLAIN
        text = ''
        tmp_packages = OrderedDict()
        columns = self._config.get_columns()
        widths = {}
        for _pkg in packages.values():
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
        return text

    def output_format_module(self, packages, esc_path=False):
        """
        Create out with child first position
        """

        def create_ordered_list(packages_):
            """
            Recursive for package.packages
            """
            list_ = []
            for _pkg_name in packages_:
                _pkg = packages_[_pkg_name]
                if _pkg and _pkg.packages:
                    list_.extend(create_ordered_list(_pkg.packages))
                if _pkg:
                    _pkg_params = _pkg.get_params(self._columns, True)
                    _res_item = {}
                    for item in self._output_config['columns']:
                        name = item['name'].format(OutFormat(item['column']))
                        value = _pkg_params.get(item['column'], '')
                        if not isinstance(value, (list, dict, tuple)):
                            try:
                                value = item['value'].format(
                                    OutFormat(value, (item['column'] == 'path') if esc_path else False))
                            except:
                                value = ''
                        # TODO: implement this:
                        # if not value:
                        #     try:
                        #         value = item['value'].format(OutFormat(_pkg.get_params('', True)))
                        #     except:
                        #         pass
                        _res_item[name] = value
                    list_.append(_res_item)
            return list_

        result_list = create_ordered_list(packages, )

        if self._output_config['type'] == LIST:
            return result_list

        result = OrderedDict()
        for item in result_list:
            # TODO: Error handling
            name = item[self._output_config['key']]
            if self._output_config['value']:
                value = item[self._output_config['value']]
            else:
                value = OrderedDict([(k, v) for k, v in item.items() if k != self._output_config['key']])

            result[name] = value

        return result

    @register_output_format('python')
    def output_format_python(self, packages, **kwargs):
        def get_value(_v):
            if isinstance(_v, (int, float, bool)):
                _res = '{}'.format(str(_v))
            elif isinstance(_v, (dict, tuple, list)):
                _res = '{}'.format(str(_v))
            else:
                _res = "'{}'".format(str(_v))
            return _res

        def items_iter(_dict_or_list):
            if isinstance(_dict_or_list, dict):
                for k in sorted(_dict_or_list, key=lambda x: str(x).lower()):
                    yield k
            else:
                for k in _dict_or_list:
                    yield k

        result = '# -*- coding: utf-8 -*-\n\n'
        res = ''
        dict_or_list = self.output_format_module(packages, True)
        for item in items_iter(dict_or_list):
            if self._output_config['type'] == LIST:
                res += '    {\n'
                for k, v in item.items():
                    res += "        '{}': {},\n".format(k, get_value(v))
                res += '    },\n'
            elif self._output_config['type'] == DICT:
                res += "    '{}': ".format(item)
                if isinstance(dict_or_list[item], dict):
                    res += '{\n'
                    for k, v in dict_or_list[item].items():
                        res += "        '{}': {},\n".format(k, get_value(v))
                    res += '    },\n'
                elif isinstance(dict_or_list[item], (list, tuple)):
                    res += '[\n'
                    for v in dict_or_list[item]:
                        res += "        {},\n".format(get_value(v))
                    res += '    ],\n'
                else:  # str
                    res += "{},\n".format(get_value(dict_or_list[item]))
            else:
                res += '{} = '.format(self.get_var_name(item), get_value(dict_or_list[item]))
                if isinstance(dict_or_list[item], dict):
                    res += '{\n'
                    for k, v in dict_or_list[item].items():
                        res += "    '{}': {},\n".format(k, get_value(v))
                    res += '}\n'
                elif isinstance(dict_or_list[item], (list, tuple)):
                    res += '[\n'
                    for v in dict_or_list[item]:
                        res += "    {},\n".format(get_value(v))
                    res += ']\n'
                else:  # str
                    res += "{}\n".format(get_value(dict_or_list[item]))

        if self._output_config['type'] == LIST:
            result += '{} = [\n'.format(self._output_config['root'] or 'PACKAGES_ROOT')
            result += res
            result += ']\n'
        elif self._output_config['type'] == DICT:
            result += '{} = {}\n'.format(self._output_config['root'] or 'PACKAGES_ROOT', '{')
            result += res
            result += '}\n'
        else:
            result += res

        return result

    @register_output_format('json')
    def output_format_json(self, packages, **kwargs):
        dict_or_list = self.output_format_module(packages)
        if self._output_config['root']:
            dict_or_list = {
                self._output_config['root']: dict_or_list
            }
        # TODO: Find a proper way to avoid double backslashes in path only (or not?)
        result = json.dumps(dict_or_list, indent=True)  # .replace('\\\\', '\\')
        return result
