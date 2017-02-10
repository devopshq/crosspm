#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
    crosspm download [options]
    crosspm lock [DEPS] [DEPSLOCK] [options]
    crosspm pack <OUT> <SOURCE> [options]
    crosspm cache [size | age | clear [hard]]
    crosspm -h | --help
    crosspm --version

Options:
    <OUT>                           Output file.
    <SOURCE>                        Source directory path.
    -h, --help                      Show this screen.
    --version                       Show version.
    -L, --list                      Do not load packages and its dependencies. Just show what's found.
    -v LEVEL, --verbose=LEVEL       Set output verbosity: ({verb_level}) [default: ].
    -l LOGFILE, --log=LOGFILE       File name for log output. Log level is '{log_default}' if set when verbose doesn't.
    -c FILE, --config=FILE          Path to configuration file.
    -o OPTIONS, --options OPTIONS   Extra options.
    --deps-path=FILE                Path to file with locked dependencies [./{deps_default}]
    --depslock-path=FILE            Path to file with locked dependencies [./{deps_lock_default}]
    --out-format=TYPE               Output data format. Available formats:({out_format}) [default: {out_format_default}]
    --output=FILE                   Output file name (required if --out_format is not stdout)
    --no-fails                      Ignore fails config if possible.

"""

import logging
from docopt import docopt
import os
from crosspm import version
from crosspm.helpers.archive import Archive
from crosspm.helpers.config import (
    CROSSPM_DEPENDENCY_LOCK_FILENAME,
    CROSSPM_DEPENDENCY_FILENAME,
    Config,
)
from crosspm.helpers.downloader import Downloader
from crosspm.helpers.locker import Locker
from crosspm.helpers.output import Output
from crosspm.helpers.exceptions import *

app_name = 'CrossPM (Cross Package Manager) version: {version} The MIT License (MIT)'.format(version=version)


class CrossPM(object):
    _config = None
    _args = None
    _output = None
    _ready = False
    _throw_exceptions = True
    _return_result = False

    def __init__(self, args=None, throw_exceptions=None, return_result=False):
        if throw_exceptions is not None:
            self._throw_exceptions = throw_exceptions
        elif args is not None:
            self._throw_exceptions = False
            self._return_result = return_result

        self._log = logging.getLogger('crosspm')
        self._args = docopt('{}\n{}'.format(app_name,
                                            __doc__.format(verb_level=Config.get_verbosity_level(),
                                                           log_default=Config.get_verbosity_level(0, True),
                                                           deps_default=CROSSPM_DEPENDENCY_FILENAME,
                                                           deps_lock_default=CROSSPM_DEPENDENCY_LOCK_FILENAME,
                                                           out_format=Output.get_output_types(),
                                                           out_format_default='stdout',
                                                           ),
                                            ),
                            argv=args,
                            version=version)

        if type(self._args) is str:
            if self._throw_exceptions:
                print(app_name)
                print(self._args)
                exit()

        self._ready = True

    def read_config(self):
        _deps_path = ''
        _depslock_path = self._args['--depslock-path']
        if self._args['lock']:
            if self._args['DEPS']:
                _deps_path = self._args['DEPS']
            if self._args['DEPSLOCK']:
                _depslock_path = self._args['DEPSLOCK']
        self._config = Config(self._args['--config'], self._args['--options'], self._args['--no-fails'], _depslock_path,
                              _deps_path)
        self._output = Output(self._config.output('result', None), self._config.name_column, self._config)

    def run(self):
        if self._ready:
            errorcode, msg = self.do_run(self.set_logging_level)
            self._log.info(app_name)
            errorcode, msg = self.do_run(self.check_common_args)
            if errorcode == 0:
                errorcode, msg = self.do_run(self.read_config)

                if errorcode == 0:
                    if self._args['download']:
                        errorcode, msg = self.do_run(self.download)
                        # self.download()

                    elif self._args['lock']:
                        errorcode, msg = self.do_run(self.lock)

                    elif self._args['pack']:
                        errorcode, msg = self.do_run(self.pack)

                    elif self._args['cache']:
                        errorcode, msg = self.do_run(self.cache)
        else:
            errorcode, msg = CROSSPM_ERRORCODE_WRONG_ARGS, self._args
        return errorcode, msg

    def do_run(self, func, *args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except CrosspmExceptionWrongArgs as e:
            if self._throw_exceptions:
                print(__doc__)
                self._log.critical(e.msg)
                sys.exit(e.error_code)
            else:
                return e.error_code, e.msg

        except CrosspmException as e:
            if self._throw_exceptions:
                print_stdout('')
                self._log.critical(e.msg)
                sys.exit(e.error_code)
            else:
                return e.error_code, e.msg

        except Exception as e:
            if self._throw_exceptions:
                print_stdout('')
                self._log.exception(e)
                self._log.critical('Unknown error occurred!')
                sys.exit(CROSSPM_ERRORCODE_UNKNOWN_ERROR)
            else:
                return CROSSPM_ERRORCODE_UNKNOWN_ERROR, 'Unknown error occurred!'
        return 0, res

    def check_common_args(self):
        if self._args['--output']:
            output = self._args['--output'].strip().strip("'").strip('"')
            output_abs = os.path.abspath(output)
            if os.path.isdir(output_abs):
                raise CrosspmExceptionWrongArgs(
                    '"%s" is a directory - can\'t write to it'
                )
            self._args['--output'] = output

    def set_logging_level(self):
        level_str = self._args['--verbose'].strip().lower()

        log = self._args['--log']
        if log:
            log = log.strip().strip("'").strip('"')
            log_abs = os.path.abspath(log)
            if os.path.isdir(log_abs):
                raise CrosspmExceptionWrongArgs(
                    '"%s" is a directory - can\'t write log to it'
                )
            else:
                log_dir = os.path.dirname(log_abs)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
        else:
            log_abs = None

        level = Config.get_verbosity_level(level_str or 'console')
        if level or log_abs:
            self._log.setLevel(level)
            format_str = '%(asctime)-19s [%(levelname)-9s] %(message)s'
            if level_str == 'debug':
                format_str = '%(asctime)-19s [%(levelname)-9s] %(name)-12s: %(message)s'
            formatter = logging.Formatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")

            if level:
                sh = logging.StreamHandler(stream=sys.stderr)
                sh.setLevel(level)
                # sh.setFormatter(formatter)
                self._log.addHandler(sh)

            if log_abs:
                if not level_str:
                    level = Config.get_verbosity_level(0)
                fh = logging.FileHandler(filename=log_abs)
                fh.setLevel(level)
                fh.setFormatter(formatter)
                self._log.addHandler(fh)

    def download(self):
        if self._return_result:
            params = {}
        else:
            if self._args['--out-format'] == 'stdout':
                if self._args['--output']:
                    raise CrosspmExceptionWrongArgs(
                        "unwanted argument '--output' while argument '--out-format={}'".format(
                            self._args['--out-format'],
                        ))
            elif not self._args['--output']:
                raise CrosspmExceptionWrongArgs(
                    "argument '--output' required when argument '--out-format={}'".format(
                        self._args['--out-format'],
                    ))

            params = {
                'out_format': ['--out-format', ''],
                'output': ['--output', ''],
                # 'out_prefix': ['--out-prefix', ''],
                # 'depslock_path': ['--depslock-path', ''],
            }

            for k, v in params.items():
                params[k] = self._args[v[0]] if v[0] in self._args else v[1]
                if isinstance(params[k], str):
                    params[k] = params[k].strip('"').strip("'")

        do_load = not self._args['--list']
        if do_load:
            self._config.cache.auto_clear()
        cpm_downloader = Downloader(self._config, do_load)
        # cpm_downloader = Downloader(self._config, params.pop('depslock_path'), do_load)
        packages = cpm_downloader.download_packages()

        _not_found = any(_pkg is None for _pkg in packages.values())
        if _not_found:
            raise CrosspmException(
                CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
                'Some package(s) not found.'
            )
        if do_load:
            if self._return_result:
                if str(self._return_result).lower() == 'raw':
                    return cpm_downloader.get_raw_packages()
                else:
                    return self._output.output_type_module(packages)
            else:
                self._output.write(params, packages)
        return ''

    def lock(self):

        cpm_locker = Locker(self._config)
        cpm_locker.lock_packages()

    def pack(self):
        Archive.create(self._args['<OUT>'], self._args['<SOURCE>'])

    def cache(self):
        if self._args['clear']:
            self._config.cache.clear(self._args['hard'])
        elif self._args['size']:
            self._config.cache.size()
        elif self._args['age']:
            self._config.cache.age()
        else:
            self._config.cache.info()


if __name__ == '__main__':
    app = CrossPM()
    app.run()
