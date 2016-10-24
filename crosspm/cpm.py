#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CrossPM (Cross Package Manager) version: {version} The MIT License (MIT)

Usage:
    crosspm download [options]
    crosspm promote [options]
    crosspm pack <OUT> <SOURCE> [options]
    crosspm -h | --help
    crosspm --version

Options:
    <OUT>                          Output file.
    <SOURCE>                       Source directory path.
    -h, --help                     Show this screen.
    --version                      Show version.
    -l, --list                     Do not load packages and its dependencies. Just show what's found.
    -v, --verbose                  Increase output verbosity.
    --verbosity=LEVEL              Set output verbosity level: ({verb_level}) [default: {verb_default}].
    -c=FILE, --config=FILE         Path to configuration file.
    -o OPTIONS, --options OPTIONS  Extra options.
    --depslock-path=FILE           Path to file with locked dependencies [./{deps_lock_default}]
    --out-format=TYPE              Output data format. Available formats:({out_format}) [default: {out_format_default}]
    --output=FILE                  Output file name (required if --out_format is not stdout)
    --out-prefix=PREFIX            Prefix for output variable name [default: ] (no prefix at all)
    --no-fails                     Ignore fails config if possible.

"""

# TODO: Remove 'logging' module usage
# TODO: Implement 'verbose' and 'verbosity=LEVEL' usage
import logging

from docopt import docopt
import os
import crosspm
from crosspm.helpers.archive import Archive
from crosspm.helpers.config import (
    CROSSPM_DEPENDENCY_LOCK_FILENAME,
    Config,
    get_verbosity_level,
)
from crosspm.helpers.downloader import Downloader
from crosspm.helpers.promoter import Promoter
from crosspm.helpers.output import Output
from crosspm.helpers.exceptions import *


# TODO: Upgrade exceptions handling
class App(object):
    _config = None
    _args = None
    _output = Output()

    def __init__(self):
        self._log = logging.getLogger(__name__)
        self._args = docopt(__doc__.format(version=crosspm.__version__,
                                           verb_level=get_verbosity_level(),
                                           verb_default=get_verbosity_level(0),
                                           deps_lock_default=CROSSPM_DEPENDENCY_LOCK_FILENAME,
                                           out_format=self._output.get_output_types(),
                                           out_format_default='stdout',
                                           ),
                            version=crosspm.__version__)

        if type(self._args) is str:
            print(self._args)
            exit()

    def read_config(self):
        self._config = Config(self._args['--config'], self._args['--options'], self._args['--no-fails'])

    def run(self):
        self.do_run(self.check_common_args)
        self.do_run(self.read_config)

        if self._args['download']:
            self.do_run(self.download)
            # self.download()

        elif self._args['promote']:
            self.do_run(self.promote)

        elif self._args['pack']:
            self.do_run(self.pack)

    def do_run(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except CrosspmExceptionWrongArgs as e:
            print(__doc__)
            self._log.critical(e.msg)
            sys.exit(e.error_code)

        except CrosspmException as e:
            print_stdout('')
            self._log.critical(e.msg)
            sys.exit(e.error_code)

        except Exception as e:
            print_stdout('')
            self._log.exception(e)
            self._log.critical('Unknown error occurred!')
            sys.exit(CROSSPM_ERRORCODE_UNKNOWN_ERROR)

    def check_common_args(self):
        log_level = ''

        if self._args['--verbose'] and self._args['--verbosity']:
            raise CrosspmExceptionWrongArgs(
                'implicit requirements --verbose and --verbosity'
            )

        if self._args['--output']:
            output = self._args['--output'].strip().strip("'").strip('"')
            output_abs = os.path.abspath(self._args['--output'].strip().strip("'").strip('"'))
            if os.path.isdir(output_abs):
                raise CrosspmExceptionWrongArgs(
                    '"%s" is a directory - can\'t write to it'
                )
            self._args['--output'] = output

        if self._args['--verbose']:
            log_level = 'info'

        elif self._args['--verbosity']:
            log_level = self._args['--verbosity']

        self.set_logging_level(log_level)

    @staticmethod
    def set_logging_level(value):
        format_str = '%(levelname)s:%(message)s'

        if value.lower() == 'debug':
            format_str = '%(levelname)s:%(name)s:%(message)s'

        logging.basicConfig(
            format=format_str,
            level=get_verbosity_level(value),
        )

    def download(self):

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
            'out_prefix': ['--out-prefix', ''],
            'depslock_path': ['--depslock-path', ''],
        }

        for k, v in params.items():
            params[k] = self._args[v[0]] if v[0] in self._args else v[1]

        do_load = not self._args['--list']
        cpm_downloader = Downloader(self._config, params.pop('depslock_path'), do_load)
        packages = cpm_downloader.download_packages()

        _not_found = any(_pkg is None for _pkg in packages.values())
        if _not_found:
            raise CrosspmException(
                CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
                'Some package(s) not found.'
            )
        if do_load:
            self._output.write(params, packages)

    def promote(self):
        cpm_promoter = Promoter(self._config)
        cpm_promoter.promote_packages()

    def pack(self):
        Archive.create(self._args['<OUT>'], self._args['<SOURCE>'])


if __name__ == '__main__':
    app = App()
    app.run()
