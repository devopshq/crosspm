# -*- coding: utf-8 -*-

import logging
import os
import re
from crosspm.helpers.exceptions import *

log = logging.getLogger(__name__)
_output_format_map = {}


def register_output_format(name):
    def check_decorator(fn):
        _output_format_map[name] = fn

        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return check_decorator


class Output(object):
    _prefix = ''

    def get_var_name(self, pkg_name):
        result = '{}{}_ROOT'.format(self._prefix, pkg_name)

        result = result.upper()
        result = result.replace('-', '_')
        result = re.sub(r'[^A-Z_0-9]', '', result)

        if not result[0].isalpha() or '_' == result[0]:
            result = '_' + result

        return result

    @staticmethod
    def write_to_file(text, out_file_path):
        out_file_path = os.path.realpath(out_file_path)
        out_dir_path = os.path.dirname(out_file_path)

        if not os.path.exists(out_dir_path):
            log.info('mkdirs [%s] ...', out_dir_path)
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

    def write(self, params, packages):
        if params['out_format'] not in _output_format_map:
            raise CrosspmException(
                CROSSPM_ERRORCODE_UNKNOWN_OUT_TYPE,
                'unknown output type: [{}]'.format(params['out_format']),
            )

        f = _output_format_map[params['out_format']]
        result = f(self, packages)

        if result:
            out_dir = os.path.dirname(params['output'])
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            self.write_to_file(result, params['output'])
            log.info(
                'Write packages info to file [%s]\n\tcontent:\n\t%s',
                params['output'],
                result,
            )

    @register_output_format('stdout')
    def output_type_stdout(self, packages):
        # sys.stdout.write('\n')
        # sys.stdout.flush()
        for _pkg in packages.values():
            if _pkg:
                _pkg_name, _pkg_path = _pkg.get_name_and_path()
                sys.stdout.write('{}{}: {}\n'.format(self._prefix, _pkg_name, _pkg_path))
                sys.stdout.flush()
        return None

    @register_output_format('shell')
    def output_type_shell(self, packages):
        result = '\n'
        for _pkg in packages.values():
            if _pkg:
                _pkg_name, _pkg_path = _pkg.get_name_and_path()
                result += "{}='{}'\n".format(self.get_var_name(_pkg_name), _pkg_path)

        result += '\n'
        return result

    @register_output_format('cmd')
    def output_type_cmd(self, packages):
        result = '\n'
        for _pkg in packages.values():
            if _pkg:
                _pkg_name, _pkg_path = _pkg.get_name_and_path()
                result += 'set {}={}\n'.format(self.get_var_name(_pkg_name), _pkg_path)

        result += '\n'
        return result

    @register_output_format('python')
    def output_type_python(self, packages):
        result = '# -*- coding: utf-8 -*-\n\n'
        packages_dict_str = ''
        for _pkg in packages.values():
            if _pkg:
                _pkg_name, _pkg_path = _pkg.get_name_and_path()
                _pkg_name = self.get_var_name(_pkg_name)
                result += "{} = '{}'\n".format(_pkg_name, _pkg_path)
                packages_dict_str += "\t'{}': '{}',\n".format(_pkg_name, _pkg_path)

        result += '\nPACKAGES_ROOT = {\n' + packages_dict_str + '}\n'
        return result

    @register_output_format('json')
    def output_type_json(self, packages):
        result = '{\n'
        n = len(packages)
        for i, _pkg in enumerate(packages.values()):
            if _pkg:
                _pkg_name, _pkg_path = _pkg.get_name_and_path()
                comma = ',' if i < n - 1 else ''
                result += "\t\"{}\": \"{}\"{}\n".format(self.get_var_name(_pkg_name), _pkg_path, comma)

        result += '}\n'
        return result
