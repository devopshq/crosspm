#!/usr/bin/env python
# -*- coding: utf-8 -*-


# The MIT License (MIT)
#
# Copyright (c) 2015 Iaroslav Akimov <iaroslavscript@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import argparse
import collections
import logging
import sys

import crosspm
import crosspm.api as api
from crosspm.helpers import pm_common
from crosspm.helpers import pm_download_output


log = logging.getLogger( __name__ )


def get_verbosity_levels():

    return collections.OrderedDict([
        ( 'critical', logging.CRITICAL, ),
        ( 'error',    logging.ERROR, ),
        ( 'warning',  logging.WARNING, ),
        ( 'info',     logging.INFO, ),
        ( 'debug',    logging.DEBUG, ),
    ])

def get_default_verbosity_level():

    return 'warning'

def make_parser():

    # create the top-level parser
    parser = argparse.ArgumentParser(
        prog='PROG',
        description="CrossPM (Cross Package Manager) version: {version} The MIT License (MIT)".format(
            version=crosspm.__version__,
        ),
        epilog="Copyright (c) 2016 Iaroslav Akimov <iaroslavscript@gmail.com> site: https://github.com/devopshq/crosspm"
    )

    parser.add_argument( '--version',
        action='version',
        version=crosspm.__version__,
    )

    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the subcommands
    make_parser_download( subparsers )
    make_parser_promote( subparsers )
    make_parser_pack( subparsers )

    return parser

def add_common_arguments(parser):

    # TODO: find out why add_parser(parents) raise error when used with subparsers
    parser.add_argument( '-v', '--verbose',
        action='store_true',
        help='increase output verbosity (default: %(default)s)',
    )

    parser.add_argument( '--verbosity',
        choices=get_verbosity_levels().keys(),
        help='set output verbosity level: [%(choices)s] (default: {})'.format(
            get_default_verbosity_level(),
        ),
        metavar='LEVEL',
    )

def make_parser_download(subparsers):

    parser = subparsers.add_parser( 'download',
        help='a download help',
    )

    parser.set_defaults(
        check_args=check_args_cmd_download,
        call_cmd=cmd_download,
    )

    add_common_arguments( parser )

    parser.add_argument( 'osname',
        metavar='<OS>',
        help='target operation system name',
    )
    parser.add_argument( 'arch',
        metavar='<ARCH>',
        help='target build architecture type',
    )
    parser.add_argument( 'compiler',
        metavar='<CL>',
        help='current compiler name',
    )

    group_general = parser.add_argument_group( 'general arguments' )

    group_general.add_argument( '-c', '--config',
        metavar='FILE',
        help='path to configuration file',
    )

    group_general.add_argument( '-o', '--option',
        action='append',
        help='extra options',
    )

    group_general.add_argument( '--depslock-path',
        metavar='FILE',
        default=pm_common.CROSSPM_DEPENDENCYLOCK_FILENAME,
        help='path to file with locked dependencies (default: ./%(default)s)'
    )

    group_output = parser.add_argument_group( 'output arguments' )

    group_output.add_argument( '--out-format',
        metavar='TYPE',
        choices=pm_download_output.get_output_types(),
        default='stdout',
        help='output data format. Avalible format types:[%(choices)s] (default: %(default)s)',
    )
    group_output.add_argument( '--output',
        metavar='FILE',
        help='output file name (required if --out_format is not stdout)',
    )
    group_output.add_argument( '--out-prefix',
        metavar='PREFIX',
        default='',
        help='prefix for output variable name (default: no prefix at all)',
    )

def make_parser_promote(subparsers):

    parser = subparsers.add_parser( 'promote',
        help='a promote help',
    )

    parser.set_defaults(
        check_args=None,
        call_cmd=cmd_promote,
    )

    add_common_arguments( parser )

    group_general = parser.add_argument_group( 'general arguments' )

    group_general.add_argument( '-c', '--config',
        metavar='FILE',
        help='path to configuration file',
    )

    group_general.add_argument( '-o', '--option',
        action='append',
        help='extra options',
    )

def make_parser_pack(subparsers):

    parser = subparsers.add_parser( 'pack',
        help='a pack help',
    )

    parser.set_defaults(
        check_args=None,
        call_cmd=cmd_pack,
    )

    parser.add_argument( 'out',
        metavar='<OUT>',
        help='output file',
    )

    parser.add_argument( 'src',
        metavar='<SOURCE>',
        help='source directory path',
    )

def check_args_cmd_download(args):

    if 'stdout' == args.out_format:

        if args.output:

            raise pm_common.CrosspmExceptionWrongArgs(
                "no need argument '--output' when argument '--out-format={}'".format(
                    args.out_format,
            ))

    elif not args.output:

        raise pm_common.CrosspmExceptionWrongArgs(
            "argument '--output' required when argument '--out-format={}'".format(
                args.out_format,
        ))

def cmd_download(args):

    cpm_downloader = api.CrosspmDownloader({
        'osname':        args.osname,
        'arch':          args.arch,
        'compiler':      args.compiler,
        'out_format':    args.out_format,
        'output':        args.output,
        'out_prefix':    args.out_prefix,
        'depslock_path': args.depslock_path,
    })

    cpm_downloader.set_config_from_file( args.config )
    cpm_downloader.get_packages()

def cmd_promote(args):

    cpm_promoter = api.CrosspmPromoter()

    cpm_promoter.set_config_from_file( args.config )
    cpm_promoter.promote_packages()

def cmd_pack(args):

    pm_common.createArchive( args.out, args.src )

def set_logging_level(value):

    format_str='%(levelname)s:%(message)s'

    if 'debug' == value:

        format_str='%(levelname)s:%(name)s:%(message)s'

    logging.basicConfig(
        format=format_str,
        level=get_verbosity_levels().get( value ),
    )

def check_common_args(args):

    log_level = get_default_verbosity_level()

    if args.verbose  and  args.verbosity:
        raise pm_common.CrosspmExceptionWrongArgs(
            'implicit requirements --verbose and --verbosity'
        )

    elif args.verbose:
        log_level = 'info'

    elif args.verbosity:
        log_level = args.verbosity

    set_logging_level( log_level )

def check_args(args):

    check_common_args( args )

    if args.check_args is not None:

        args.check_args( args )

def main():

    parser = make_parser()

    try:
        args = parser.parse_args()

    except SystemExit:
        sys.exit( pm_common.CROSSPM_ERRORCODE_WRONGARGS )

    try:
        if not vars( args ):
            raise pm_common.CrosspmExceptionWrongArgs( 'too few arguments' )

        check_args( args )
        args.call_cmd( args )

    except pm_common.CrosspmExceptionWrongArgs as e:

        parser.print_usage()
        log.critical( e.msg )
        sys.exit( e.error_code )

    except pm_common.CrosspmException as e:

        log.critical( e.msg )
        sys.exit( e.error_code )

    except Exception as e:

        log.exception( e )
        log.critical( 'Unknown error occurred!' )
        sys.exit( pm_common.CROSSPM_ERRORCODE_UNKNOWN_ERROR )


if __name__ == '__main__':

    main()
