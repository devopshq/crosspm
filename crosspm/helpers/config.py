# -*- coding: utf-8 -*-
import os
import sys
import logging
import json
import platform
import yaml
from crosspm.helpers.exceptions import *
from crosspm.helpers.parser import Parser
from crosspm.helpers.source import Source
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
ENVIRONMENT_CONFIG_PATH = 'CROSSPM_CONFIG_PATH'
ENVIRONMENT_CACHE_ROOT = 'CROSSPM_CACHE_ROOT'
CROSSPM_DEPENDENCY_LOCK_FILENAME = 'cpm.manifest'  # former 'dependencies.txt.lock'
CROSSPM_ADAPTERS_NAME = 'adapters'
CROSSPM_ADAPTERS_DIR = os.path.join(CROSSPM_ROOT_DIR, CROSSPM_ADAPTERS_NAME)

disable_warnings()


class Config(object):
    _sources = []
    _adapters = {}
    _parsers = {}
    _defaults = {}
    _columns = []
    _not_columns = {}
    _options = {}
    _values = {}
    name_column = ''
    deps_lock_file_name = ''
    windows = WINDOWS

    def __init__(self, config_file_name='', cmdline=''):
        self._log = logging.getLogger(__name__)
        self._config_file_name = self.find_config_file(config_file_name)
        config_data = self.read_config_file()
        self.parse_config(config_data)
        self.parse_options(cmdline)

        # init not columns:
        self.init_not_columns()

    @staticmethod
    def get_crosspm_cache_root():
        root = os.getenv(ENVIRONMENT_CACHE_ROOT)
        if not root:
            home_dir = os.getenv('APPDATA') if WINDOWS else os.getenv('HOME')
            root = os.path.join(home_dir, '.crosspm')
        return root

    def find_config_file(self, config_file_name=''):
        if not config_file_name:
            config_path_env = os.getenv(ENVIRONMENT_CONFIG_PATH)
            if config_path_env:
                if config_path_env in DEFAULT_CONFIG_PATH:
                    DEFAULT_CONFIG_PATH.remove(config_path_env)
                DEFAULT_CONFIG_PATH.insert(0, config_path_env)

            _def_conf_file = [DEFAULT_CONFIG_FILE] if type(DEFAULT_CONFIG_FILE) is str else DEFAULT_CONFIG_FILE
            for config_path in DEFAULT_CONFIG_PATH:
                for _conf_file in _def_conf_file:
                    config_file_name = os.path.join(config_path, _conf_file)
                    if os.path.isfile(config_file_name):
                        break
                    else:
                        config_file_name = ''
                if config_file_name:
                    break
        else:
            if not os.path.isfile(config_file_name):
                config_file_name = ''

        if config_file_name == '':
            raise CrosspmException(
                CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
                'Config file does not found',
            )

        self._log.info('Found config file at working directory [%s]', config_file_name)
        return os.path.realpath(config_file_name)

    def read_config_file(self):
        self._log.info('Reading config file... [%s]', self._config_file_name)
        _ext = os.path.splitext(self._config_file_name)[1].lower()
        _is_yaml = True
        if _ext in ['.yaml', '.yml']:
            _is_yaml = True
        elif _ext == '.json':
            _is_yaml = False
        else:
            with open(self._config_file_name) as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('{'):
                        _is_yaml = False  # Assuming JSON format
                        break

        try:
            with open(self._config_file_name) as f:
                if _is_yaml:
                    result = yaml.safe_load(f)
                else:
                    result = json.loads(f.read())

        except Exception as e:
            self._log.exception(e)
            code = CROSSPM_ERRORCODE_CONFIG_IO_ERROR
            msg = 'Error reading config file: [{}]'.format(self._config_file_name)
            raise CrosspmException(code, msg) from e

        return result

    def parse_config(self, config_data):
        # init cpm parameters
        for x in ['cpm', 'crosspm']:
            if x in config_data:
                self.init_cpm_config(config_data[x])
                break

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

                if _src['type'] not in self._adapters.keys():
                    code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
                    msg = 'Adapter [{}] does not found!'.format(_src['type'])
                    self._log.exception(msg)
                    raise CrosspmException(code, msg)

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

    def init_not_columns(self):
        # gather items from options
        # include options here even if they are columns also
        self._not_columns = {k: v for k, v in self._options.items()}

        # gather items from defaults
        self._not_columns.update({k: v for k, v in self._defaults.items() if k not in self._not_columns})

        # gather items from parsers
        for _parser in self._parsers.values():
            self._not_columns.update({k: None for k in _parser.get_vars() if k not in self._not_columns})

    def init_cpm_config(self, crosspm):
        def param(param_name, param_default):
            return crosspm[param_name] if param_name in crosspm else param_default

        self.deps_lock_file_name = param('dependencies', CROSSPM_DEPENDENCY_LOCK_FILENAME)

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
                self._log.warning(msg)

        if _remove:
            sys.path.remove(_base_dir)
        os.chdir(_cwd)

    def parse_options(self, cmdline):
        try:
            _cmdline = {x[0]: x[1] for x in [x.strip().split('=') for x in cmdline.split(',')] if len(x) > 1}
        except:
            _cmdline = {}
        _remove = []
        for k, v in self._options.items():

            # if option has cmdline name, try to fetch a value from command line by cmdline name
            if 'cmdline' in v:
                if v['cmdline'] in _cmdline:
                    self._options[k] = _cmdline[v['cmdline']]

            # if option hasn't cmdline name, try to fetch a value from command line by option's name
            elif k in _cmdline:
                self._options[k] = _cmdline[k]

            # if option is still not filled, try to get a value from environment by env name
            if type(self._options[k]) is not str:
                _env = os.getenv(v['env'])
                if _env:
                    self._options[k] = _env

                # if option is still not filled, just remove it from dict
                else:
                    _remove.append(k)
        for k in _remove:
            self._options.pop(k, None)

    def sources(self):
        for _src in self._sources:
            yield _src

    def check_column_value(self, i, v, get_list=False):
        k = self._columns[i]
        if k in self._options:
            v = self._options[k]
        if v is None:
            if k in self._defaults:
                v = self._defaults[k]
        return [k, v] if get_list else {k: v}

    def get_column_name(self, i):
        return self._columns[i] if len(self._columns) - 1 >= i else None

    def complete_params(self, _vars):
        _vars.update({k: v for k, v in self._not_columns.items() if k not in _vars})
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


def get_verbosity_level(level=None):
    levels = (
        ('critical', logging.CRITICAL, False),
        ('error', logging.ERROR, False),
        ('warning', logging.WARNING, True),
        ('info', logging.INFO, False),
        ('debug', logging.DEBUG, False),
    )
    if level is None:
        return ', '.join(x[0] for x in levels)

    default = None
    for x in levels:
        if type(level) == 'str':
            if x[0] == level.lower():
                return x[1]
        if x[2]:
            default = x[1]

    return default
