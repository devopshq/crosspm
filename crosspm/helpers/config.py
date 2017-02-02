# -*- coding: utf-8 -*-
import os
import logging
import json
import platform
import yaml
from crosspm.helpers.exceptions import *
from crosspm.helpers.parser import Parser
from crosspm.helpers.source import Source
from crosspm.helpers.cache import Cache

from requests.packages.urllib3 import disable_warnings

WINDOWS = (platform.system().lower() == 'windows') or (os.name == 'nt')
DEFAULT_CONFIG_FILE = ('crosspm.yaml', 'crosspm.yml', 'crosspm.json',)
USER_HOME_DIR = os.path.expanduser('~')
CROSSPM_ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_CONFIG_PATH = [
    './',
    '~/',
    '~/.crosspm',
    '/etc/crosspm',
    CROSSPM_ROOT_DIR,
] if not WINDOWS else [
    './',
    os.path.realpath(os.path.join(os.path.splitdrive(USER_HOME_DIR)[0], '/')),
    os.path.realpath(os.path.join(USER_HOME_DIR, '.crosspm')),
    os.path.realpath(os.path.join(os.getenv('APPDATA'), 'crosspm')),
    CROSSPM_ROOT_DIR,
]
GLOBAL_CONFIG_FILE = ['crosspm_global.yaml', 'global.yaml']
GLOBAL_CONFIG_PATH = [
    '/etc/crosspm',
] if not WINDOWS else [
    '{system_drive}',
    '{all_users}\\crosspm',
    '{program_data}\\crosspm',
]

ENVIRONMENT_CONFIG_PATH = 'CROSSPM_CONFIG_PATH'
CROSSPM_DEPENDENCY_FILENAME = 'dependencies.txt'  # maybe 'cpm.manifest'
CROSSPM_DEPENDENCY_LOCK_FILENAME = CROSSPM_DEPENDENCY_FILENAME  # 'dependencies.txt.lock'
CROSSPM_ADAPTERS_NAME = 'adapters'
CROSSPM_ADAPTERS_DIR = os.path.join(CROSSPM_ROOT_DIR, CROSSPM_ADAPTERS_NAME)

disable_warnings()


class Config(object):
    _config_path_env = []
    _sources = []
    _adapters = {}
    _parsers = {}
    _defaults = {}
    _columns = []
    _not_columns = {}
    _options = {}
    _values = {}
    _output = {}
    _solid = {}
    _fails = {}
    cache = None
    no_fails = False
    name_column = ''
    deps_file_name = ''
    deps_lock_file_name = ''
    windows = WINDOWS
    crosspm_cache_root = ''
    depslock_path = ''

    def __init__(self, config_file_name='', cmdline='', no_fails=False, depslock_path='', deps_path=''):
        self._log = logging.getLogger('crosspm')
        self.init_env_config_path()

        cpm_conf_name = ''
        if deps_path:
            deps_path = deps_path.strip().strip('"').strip("'")
            self.deps_path = os.path.realpath(os.path.expanduser(deps_path))
            if not cpm_conf_name:
                cpm_conf_name = self.get_cpm_conf_name(deps_path)
            if os.path.isfile(deps_path):
                config_path_tmp = os.path.dirname(deps_path)
            else:
                config_path_tmp = deps_path
            if config_path_tmp not in DEFAULT_CONFIG_PATH:
                DEFAULT_CONFIG_PATH.append(config_path_tmp)

        if depslock_path:
            depslock_path = depslock_path.strip().strip('"').strip("'")
            self.depslock_path = os.path.realpath(os.path.expanduser(depslock_path))
            if not cpm_conf_name:
                cpm_conf_name = self.get_cpm_conf_name(depslock_path)
            if os.path.isfile(depslock_path):
                config_path_tmp = os.path.dirname(depslock_path)
            else:
                config_path_tmp = depslock_path
            if config_path_tmp not in DEFAULT_CONFIG_PATH:
                DEFAULT_CONFIG_PATH.append(config_path_tmp)

        self._config_file_name = self.find_config_file(config_file_name, cpm_conf_name)
        self._global_config_file_name = self.find_global_config_file()
        if self._global_config_file_name:
            config_data = self.read_config_file(True)
            _override = config_data.pop('override', True)
            if isinstance(_override, str):
                if _override.lower() in ['0', 'no', '-', 'false']:
                    _override = False
            try:
                _override = bool(_override)
            except:
                _override = True
        else:
            config_data = {}
            _override = False
        if _override:
            config_data.update({k: v for k, v in self.read_config_file().items() if k not in config_data})
            self._log.debug('Overriding config file values with global config.')
        else:
            config_data.update(self.read_config_file())

        self.no_fails = no_fails
        self.parse_config(config_data, cmdline)
        self.cache = Cache(self, self.cache)
        # self._fails = {}

    def get_cpm_conf_name(self, deps_filename=''):
        if not deps_filename:
            deps_filename = self.depslock_path
        result = ''
        if os.path.isfile(deps_filename):
            try:
                with open(deps_filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('#'):
                            line = [x.strip().strip('"').strip("'") for x in line.strip('#').split('=') if x]
                            if len(line) > 1:
                                if line[0].lower() == 'cpmconfig':
                                    result = line[1].split('#')[0].strip('"').strip("'")
                                    break
            except:
                pass
        return result

    def init_env_config_path(self):
        self._config_path_env = [x for x in os.getenv(ENVIRONMENT_CONFIG_PATH, '').split(';') if x]
        for config_path_env in self._config_path_env:
            config_path_tmp = os.path.dirname(config_path_env) if os.path.isfile(config_path_env) else config_path_env
            if config_path_tmp in DEFAULT_CONFIG_PATH:
                DEFAULT_CONFIG_PATH.remove(config_path_tmp)
            DEFAULT_CONFIG_PATH.insert(0, config_path_tmp)

    def find_global_config_file(self):
        args = {}
        _win_disk = self.get_windows_system_disk()
        if WINDOWS:
            args = {
                'system_drive': _win_disk,
                'all_users': os.getenv('AllUsersProfile', os.path.join(_win_disk, 'Users\\All Users')),
                'program_data': os.getenv('ProgramData', os.path.join(_win_disk, 'ProgramData')),
            }

        for config_path_env in self._config_path_env:
            if os.path.isdir(config_path_env):
                if config_path_env in GLOBAL_CONFIG_PATH:
                    GLOBAL_CONFIG_PATH.remove(config_path_env)
                GLOBAL_CONFIG_PATH.insert(0, config_path_env)

        for config_path in GLOBAL_CONFIG_PATH:
            try:
                _path = config_path.format(**args).strip().strip("'").strip('"')
            except:
                _path = ''
            if _path:
                for config_name in GLOBAL_CONFIG_FILE:
                    _file = os.path.realpath(os.path.expanduser(os.path.join(_path, config_name)))
                    if os.path.isfile(_file):
                        return _file
        return ''

    def find_cpmconfig(self, conf_name=''):
        conf_path_add = ''
        try:
            _temp = __import__('cpmconfig.cpmconfig', globals(), locals(), ['App'], 0)
            cpm_find = _temp.App.find
            _temp_conf = __import__('cpmconfig.conf', globals(), locals(), ['conf', 'conf_file', 'conf_path'], 0)
            conf_path = getattr(_temp_conf, 'conf_path', '')
            if not conf_path:
                conf_file = getattr(_temp_conf, 'conf_file', '')
                if not conf_file:
                    conf = getattr(_temp_conf, 'conf', '')
                    if conf:
                        conf_path = cpm_find(None, conf)[2]
                else:
                    conf_path = cpm_find(None, conf_file)[2]
            if conf_name:
                conf_path_add = cpm_find(None, conf_name)[2]

        except:
            conf_path = ''
        if conf_path and not os.path.isfile(conf_path):
            conf_path = ''
        if conf_path_add and not os.path.isfile(conf_path_add):
            conf_path_add = ''
        return conf_path, conf_path_add

    def find_config_file(self, config_file_name='', cpm_conf_name=''):
        if not config_file_name:
            ind = 0
            for config_path_env in self._config_path_env:
                if os.path.isfile(config_path_env):
                    if config_path_env in DEFAULT_CONFIG_PATH:
                        DEFAULT_CONFIG_PATH.remove(config_path_env)
                    DEFAULT_CONFIG_PATH.insert(ind, config_path_env)
                    ind += 1

            cpm_file_default, cpm_file_deps = self.find_cpmconfig(cpm_conf_name)
            if cpm_file_deps:
                DEFAULT_CONFIG_PATH.insert(ind, cpm_file_deps)

            _def_conf_file = [DEFAULT_CONFIG_FILE] if type(DEFAULT_CONFIG_FILE) is str else DEFAULT_CONFIG_FILE
            for config_path in DEFAULT_CONFIG_PATH:
                config_path = config_path.strip().strip("'").strip('"')
                config_path = os.path.realpath(os.path.expanduser(config_path))
                for _conf_file in _def_conf_file:
                    config_file_name = os.path.realpath(os.path.join(config_path, _conf_file)) if os.path.isdir(
                        config_path) else config_path
                    if os.path.isfile(config_file_name):
                        break
                    else:
                        config_file_name = ''
                if config_file_name:
                    break

            if not config_file_name:
                config_file_name = cpm_file_default
            if config_file_name:
                self._log.info('Found config file [%s]', config_file_name)
        else:
            config_file_name = config_file_name.strip().strip("'").strip('"')
            config_file_name = os.path.realpath(os.path.expanduser(config_file_name))
            self._log.info('Check config file [%s]', config_file_name)
            if not os.path.isfile(config_file_name):
                config_file_name = ''
            else:
                config_path_tmp = os.path.dirname(config_file_name)
                if config_path_tmp not in DEFAULT_CONFIG_PATH:
                    DEFAULT_CONFIG_PATH.append(config_path_tmp)

        if config_file_name == '':
            raise CrosspmException(
                CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
                'Config file does not found',
            )

        return config_file_name

    def read_config_file(self, _global=False):
        if _global:
            _config_file_name = self._global_config_file_name
            self._log.info('Reading global config file...')
        else:
            _config_file_name = self._config_file_name
            self._log.info('Reading config file... [%s]', _config_file_name)
        _ext = os.path.splitext(_config_file_name)[1].lower()
        _is_yaml = True
        if _ext in ['.yaml', '.yml']:
            _is_yaml = True
        elif _ext == '.json':
            _is_yaml = False
        else:
            with open(_config_file_name) as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('{'):
                        _is_yaml = False  # Assuming JSON format
                        break

        try:
            if _is_yaml:
                result = self.load_yaml(_config_file_name)
            else:
                with open(_config_file_name) as f:
                    result = json.loads(f.read())

        except Exception as e:
            self._log.exception(e)
            code = CROSSPM_ERRORCODE_CONFIG_IO_ERROR
            msg = 'Error reading config file: [{}]'.format(self._config_file_name)
            raise CrosspmException(code, msg) from e

        return result

    def find_import_file(self, import_file_name=''):
        res_file_name = ''
        if import_file_name:
            for config_path in [''] + DEFAULT_CONFIG_PATH:
                if config_path:
                    config_path = config_path.strip().strip("'").strip('"')
                    config_path = os.path.realpath(os.path.expanduser(config_path))
                if config_path == '' or os.path.isdir(config_path):
                    res_file_name = os.path.realpath(
                        os.path.expanduser(import_file_name) if config_path == '' else
                        os.path.join(config_path, import_file_name))
                    if os.path.isfile(res_file_name):
                        break
                    else:
                        res_file_name = ''
                else:
                    res_file_name = ''

            if res_file_name == '':
                raise CrosspmException(
                    CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
                    'Config import file "{}" does not found'.format(import_file_name),
                )

        return res_file_name

    def load_yaml(self, _config_file_name):
        result = {}
        yaml_imports = ''
        yaml_content = ''
        with open(_config_file_name) as f:
            for line in f:
                if (not yaml_imports) and (not yaml_content):
                    line_one = line.strip().replace(' ', '').lower()
                    if line_one.startswith('import:'):
                        yaml_imports += line
                    elif len(line_one) > 0:
                        yaml_content += line
                elif yaml_imports and not yaml_content:
                    if line.startswith((' ', '\t',)):
                        yaml_imports += line
                    elif line.strip():
                        yaml_content += line
                else:
                    yaml_content += line
        if yaml_imports:
            data_imports = yaml.safe_load(yaml_imports)
            yaml_content_pre = ''
            if 'import' in data_imports:
                if type(data_imports['import']) is str:
                    data_imports['import'] = [data_imports['import']]
                if type(data_imports['import']) in (list, tuple):
                    for _import_file_name in data_imports['import']:
                        _import_file_name = self.find_import_file(_import_file_name)
                        if _import_file_name:
                            with open(_import_file_name) as f:
                                for line in f:
                                    yaml_content_pre += line
                            yaml_content_pre += '\n'
            yaml_content = yaml_content_pre + yaml_content
        if yaml_content:
            result = yaml.safe_load(yaml_content)
        return result

    def parse_config(self, config_data, cmdline):
        # init parsers
        if 'parsers' in config_data:
            self.init_parsers(config_data['parsers'])

        # init columns
        if 'columns' in config_data:
            self._columns = []
            _name_index = 0
            for i, _col in enumerate([x for x in [x.strip().split(' ') for x in config_data['columns'].split(',')]]):
                if _col[0][0] == '*':
                    _name_index = i
                    _col = [_col[0][1:]]
                self._columns += _col
            self.name_column = self._columns[_name_index]

        # init available values for columns
        if 'values' in config_data:
            self._values = config_data['values']

        # init options
        if 'options' in config_data:
            self._options = config_data['options']

        # init default values for columns
        if 'defaults' in config_data:
            self._defaults = config_data['defaults']
        self._defaults.update({k: v['default'] for k, v in self._options.items() if k not in self._defaults})

        # init solid
        if 'solid' in config_data:
            self._solid = config_data['solid']
            if 'ext' in self._solid and not isinstance(self._solid['ext'], (list, tuple)):
                self._solid['ext'] = [self._solid['ext']]

        # init fails
        if 'fails' in config_data:
            self._fails = config_data['fails']

        # init output
        if 'output' in config_data:
            self._output = config_data['output']

        # init common parameters
        _common = {}
        if 'common' in config_data:
            _common = config_data['common']

        if 'sources' in config_data:

            # init adapters
            _types = []
            if 'type' in _common:
                _types += [_common['type']]
            for _src in config_data['sources']:
                if 'type' in _src and _src['type'] not in _types:
                    _types += [_src['type']]

            self.init_adapters(_types)

            # init sources
            for _src in config_data['sources']:
                _src.update({k: v for k, v in _common.items() if k not in _src})

                if 'type' in _src:
                    if _src['type'] not in self._adapters.keys():
                        code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
                        msg = 'Adapter [{}] does not found!'.format(_src['type'])
                        self._log.exception(msg)
                        raise CrosspmException(code, msg)
                else:
                    code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
                    msg = 'Source must have type property!'
                    self._log.exception(msg)
                    raise CrosspmException(code, msg)

                if 'parser' in _src:
                    if _src['parser'] not in self._parsers.keys():
                        code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
                        msg = 'Parser [{}] does not found!'.format(_src['parser'])
                        self._log.exception(msg)
                        raise CrosspmException(code, msg)

                self._sources.append(
                    Source(
                        self._adapters[_src['type']],
                        self._parsers[_src['parser']],
                        _src
                    )
                )

        if len(self._sources) == 0:
            code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
            msg = 'No correct sources defined! Unable to process any further.'
            self._log.exception(msg)
            raise CrosspmException(code, msg)

        try:
            _cmdline = {x[0]: x[1] for x in [x.strip().split('=') for x in cmdline.split(',')] if len(x) > 1}
        except:
            _cmdline = {}

        # init cpm parameters
        for x in ['cpm', 'crosspm']:
            if x in config_data:
                # init cache:
                if 'cache' not in config_data:
                    config_data['cache'] = {}
                self.init_cpm_and_cache(config_data[x], _cmdline, config_data['cache'])
                break

        self._options = self.parse_options(self._options, _cmdline)

        # init not columns:
        self.init_not_columns()

    def init_cpm_and_cache(self, crosspm, cmdline, cache_config):
        if 'cache' not in crosspm:
            crosspm['cache'] = {}
        if 'path' in cache_config:
            crosspm['cache'] = cache_config.pop('path')
        else:
            for x in ['env', 'cmdline', 'default']:
                if x in cache_config:
                    crosspm['cache'][x] = cache_config.pop(x)

        crosspm = self.parse_options(crosspm, cmdline)

        self.deps_lock_file_name = crosspm.get('dependencies-lock', CROSSPM_DEPENDENCY_LOCK_FILENAME)
        if 'dependencies' in crosspm:
            self.deps_file_name = crosspm.get('dependencies', CROSSPM_DEPENDENCY_FILENAME)
            if 'dependencies-lock' not in crosspm:
                self.deps_lock_file_name = self.deps_file_name

        # Cache init
        self.crosspm_cache_root = crosspm.get('cache', '').strip().strip('"').strip("'")
        if not self.crosspm_cache_root:
            home_dir = os.getenv('APPDATA') if WINDOWS else os.getenv('HOME')
            self.crosspm_cache_root = os.path.join(home_dir, '.crosspm')
        self.crosspm_cache_root = os.path.realpath(os.path.expanduser(self.crosspm_cache_root))
        self.cache = cache_config

    def init_not_columns(self):
        # gather items from options
        # include options here even if they are columns also
        self._not_columns = {k: v for k, v in self._options.items()}

        # gather items from defaults
        self._not_columns.update({k: v for k, v in self._defaults.items() if k not in self._not_columns})

        # gather items from parsers
        for _parser in self._parsers.values():
            self._not_columns.update({k: None for k in _parser.get_vars() if k not in self._not_columns})

    def init_parsers(self, parsers):
        if 'common' not in parsers:
            parsers['common'] = {}
        for k, v in parsers.items():
            if k not in self._parsers:
                v.update({_k: _v for _k, _v in parsers['common'].items() if _k not in v})
                self._parsers[k] = Parser(k, v, self)
            else:
                code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
                msg = 'Config file contains multiple definitions of the same parser: [{}]'.format(k)
                self._log.exception(msg)
                raise CrosspmException(code, msg)
        if len(self._parsers) == 0:
            code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
            msg = 'Config file does not contain parsers! Unable to process any further.'
            self._log.exception(msg)
            raise CrosspmException(code, msg)

    def get_parser(self, parser_name):
        return self._parsers[parser_name] if parser_name in self._parsers else None

    def init_adapters(self, types):
        if not os.path.isdir(CROSSPM_ADAPTERS_DIR):
            code = CROSSPM_ERRORCODE_ADAPTER_ERROR
            msg = 'Adapters directory does not found!'
            self._log.exception(msg)
            raise CrosspmException(code, msg)

        _cwd = os.getcwd()
        _base_dir = os.path.dirname(CROSSPM_ROOT_DIR)
        _adapters_app = '.'.join(os.path.split(os.path.relpath(CROSSPM_ADAPTERS_DIR, _base_dir)))
        os.chdir(_base_dir)
        _remove = False
        if _base_dir not in sys.path:
            sys.path.insert(0, _base_dir)
            _remove = True

        for _file_name in os.listdir(CROSSPM_ADAPTERS_DIR):
            if _file_name.startswith(('__', 'common',)):
                continue

            _app_file_name, _ext = os.path.splitext(_file_name)
            if not _ext.startswith('.py'):
                continue
            _app_name = '.'.join((_adapters_app, _app_file_name,))

            try:
                _temp = __import__(_app_name, globals(), locals(), ['setup', 'Adapter'], 0)
                _names = _temp.setup['name']
                if type(_names) is str:
                    _names = [_names]
                self._adapters.update({k: _temp.Adapter(self) for k in _names if k in types})

            except Exception as e:
                msg = 'Error initializing adapter {}: [{}]'.format(_file_name, e)
                self._log.error(msg)

        if _remove:
            sys.path.remove(_base_dir)
        os.chdir(_cwd)

    @staticmethod
    def parse_options(options, cmdline, check_default=False):
        # try:
        #     _cmdline = {x[0]: x[1] for x in [x.strip().split('=') for x in cmdline.split(',')] if len(x) > 1}
        # except:
        #     _cmdline = {}
        _remove = []
        for k, v in options.items():
            # if option type is str, leave the value intact
            if type(options[k]) is not str:
                # if option has cmdline name, try to fetch a value from command line by cmdline name
                if 'cmdline' in v:
                    if v['cmdline'] in cmdline:
                        options[k] = cmdline[v['cmdline']]

                # if option hasn't cmdline name, try to fetch a value from command line by option's name
                elif k in cmdline:
                    options[k] = cmdline[k]

                # if option is still not filled, try to get a value from environment by env name
                if type(options[k]) is not str:
                    success = False
                    if 'env' in v:
                        _env = os.getenv(v['env'])
                        if _env:
                            options[k] = _env
                            success = True
                    # if option is still not filled, try to fill with default value if necessary
                    if not success:
                        if check_default and 'default' in v:
                            options[k] = v['default']
                            success = True
                    # if option is still not filled again, just remove it from dict
                    if not success:
                        _remove.append(k)
        for k in _remove:
            options.pop(k)
        return options

    def sources(self):
        for _src in self._sources:
            yield _src

    def check_column_value(self, i, v, get_list=False):
        if i < len(self._columns):
            k = self._columns[i]
            if k in self._options:
                v = self._options[k]
            if v is None:
                if k in self._defaults:
                    v = self._defaults[k]
        else:
            k, v = '', ''
        return [k, v] if get_list else {k: v}

    def get_column_name(self, i):
        return self._columns[i] if len(self._columns) - 1 >= i else None

    def get_columns(self):
        return self._columns

    def complete_params(self, _vars):
        _vars.update({k: v for k, v in self._not_columns.items() if k not in _vars})
        _vars.update({k: '' for k in self._columns if k not in _vars})
        return _vars

    def get_values(self, column_name):
        _res = None
        if column_name in self._values:
            _res = self._values[column_name]
        return _res

    def iter_valued_columns(self, column_names):
        for column_name in column_names:
            if column_name in self._values:
                yield column_name

    def iter_valued_columns2(self, column_names):
        for column_name in column_names:
            yield column_name, column_name in self._values

    def output(self, out_type, default):
        if out_type in self._output:
            result = self._output[out_type]
        else:
            result = default
        return result

    def get_fails(self, fail_type, default):
        return self._fails.get(fail_type, default)

    def solid(self, package):
        if 'ext' in self._solid:
            if package.ext(self._solid['ext']):
                return True
        return False

    @staticmethod
    def get_verbosity_level(level=None, text=False):
        levels = (
            ('critical', logging.CRITICAL, False),
            ('error', logging.ERROR, False),
            ('warning', logging.WARNING, False),
            ('info', logging.INFO, True),
            ('debug', logging.DEBUG, False),
        )
        if level is None:
            return ', '.join(x[0] for x in levels)

        if level == 'console':
            level = 'debug'

        default = None
        for x in levels:
            if type(level) is str:
                if x[0] == level.lower():
                    return x[1]
            elif x[2]:
                default = x[0] if text else x[1]
                break

        return default

    @staticmethod
    def get_windows_system_disk():
        result = os.getenv('SystemDrive', '')
        if not result:
            try:
                _temp = __import__('win32api', globals(), locals(), ['GetSystemDirectory'], 0)
                result = _temp.GetSystemDirectory()
                if result:
                    result = os.path.splitdrive(result)[0]
            except:
                pass
        if not result:
            result = 'C:'
        return result
