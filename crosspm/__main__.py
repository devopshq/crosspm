#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CrossPM (Cross Package Manager) version: {version} The MIT License (MIT)

Usage:
    crosspm download <OS> <ARCH> <CL> [options]
    crosspm promote [options]
    crosspm pack <OUT> <SOURCE> [options]
    crosspm -h | --help
    crosspm --version

Options:
    <OS>                        Target operation system name.
    <ARCH>                      Target build architecture type.
    <CL>                        Current compiler name.
    <OUT>                       Output file.
    <SOURCE>                    Source directory path.
    -h, --help                  Show this screen.
    --version                   Show version.
    -v, --verbose               Increase output verbosity.
    --verbosity=LEVEL           Set output verbosity level: ({verb_level}) [default: {verb_default}].
    -c=FILE, --config=FILE      Path to configuration file.
    -o=OPTION, --option=OPTION  Extra options.
    --depslock-path=FILE        Path to file with locked dependencies [default: ./{deps_lock_default}]
    --out-format=TYPE           Output data format. Available formats:({out_format}) [default: {out_format_default}]
    --output=FILE               Output file name (required if --out_format is not stdout)
    --out-prefix=PREFIX         Prefix for output variable name [default: ] (no prefix at all)

"""

from docopt import docopt
import logging
import sys

import __init__ as crosspm
import api
from helpers import pm_common
from helpers import pm_download_output

log = logging.getLogger(__name__)


def get_verbosity_level(level=None):
    levels = (
        ('critical', logging.CRITICAL, False),
        ('error', logging.ERROR, False),
        ('warning', logging.WARNING, True),
        ('info', logging.INFO, False),
        ('debug', logging.DEBUG, False),
    )
    if level is None:
        return ', '.join([x[0] for x in levels])

    default = None
    for x in levels:
        if type(level) == 'str':
            if x[0] == level.lower():
                return x[1]
        if x[2]:
            default = x[1]

    return default


def cmd_download(args):
    if args['--out-format'] == 'stdout':
        if args['--output']:
            raise pm_common.CrosspmExceptionWrongArgs(
                "unwanted argument '--output' while argument '--out-format={}'".format(
                    args['--out-format'],
                ))
    elif not args['--output']:
        raise pm_common.CrosspmExceptionWrongArgs(
            "argument '--output' required when argument '--out-format={}'".format(
                args['--out-format'],
            ))

    param = {
        'osname': ['<OS>', ''],
        'arch': ['<ARCH>', ''],
        'compiler': ['<CL>', ''],
        'out_format': ['--out-format', ''],
        'output': ['--output', ''],
        'out_prefix': ['--out-prefix', ''],
        'depslock_path': ['--depslock-path', ''],
    }

    for k, v in param.items():
        param[k] = args[v[0]] if v[0] in args else v[1]

    cpm_downloader = api.CrosspmDownloader(param)
    cpm_downloader.set_config_from_file(args['--config'])
    cpm_downloader.get_packages()


def cmd_promote(args):
    cpm_promoter = api.CrosspmPromoter()
    cpm_promoter.set_config_from_file(args['--config'])
    cpm_promoter.promote_packages()


def cmd_pack(args):
    pm_common.createArchive(args['<OUT>'], args['<SOURCE>'])


def set_logging_level(value):
    format_str = '%(levelname)s:%(message)s'

    if value.lower() == 'debug':
        format_str = '%(levelname)s:%(name)s:%(message)s'

    logging.basicConfig(
        format=format_str,
        level=get_verbosity_level(value),
    )


def check_common_args(args):
    log_level = ''

    if args['--verbose'] and args['--verbosity']:
        raise pm_common.CrosspmExceptionWrongArgs(
            'implicit requirements --verbose and --verbosity'
        )

    if args['--verbose']:
        log_level = 'info'

    elif args['--verbosity']:
        log_level = args['--verbosity']

    set_logging_level(log_level)


def main():
    args = docopt(__doc__.format(version=crosspm.__version__,
                                 verb_level=get_verbosity_level(),
                                 verb_default=get_verbosity_level(0),
                                 deps_lock_default=pm_common.CROSSPM_DEPENDENCYLOCK_FILENAME,
                                 out_format=pm_download_output.get_output_types(),
                                 out_format_default='stdout',
                                 ),
                  version=crosspm.__version__)

    if type(args) is str:
        print(args)
        exit()

    try:
        check_common_args(args)

        if args['download']:
            cmd_download(args)

        elif args['promote']:
            cmd_promote(args)

        elif args['pack']:
            cmd_pack(args)

    except pm_common.CrosspmExceptionWrongArgs as e:
        print(__doc__)
        log.critical(e.msg)
        sys.exit(e.error_code)

    except pm_common.CrosspmException as e:
        log.critical(e.msg)
        sys.exit(e.error_code)

    except Exception as e:
        log.exception(e)
        log.critical('Unknown error occurred!')
        sys.exit(pm_common.CROSSPM_ERRORCODE_UNKNOWN_ERROR)


if __name__ == '__main__':
    main()
