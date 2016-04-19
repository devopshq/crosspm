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


import sys
import argparse

import crosspm
import crosspm.api as api
from crosspm.helpers import pm_common
from crosspm.helpers import pm_download_output


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


def make_parser_download( subparsers ):

    parser = subparsers.add_parser( 'download',
        help='a download help',
    )

    parser.set_defaults(
        check_args=check_args_cmd_download,
        call_cmd=cmd_download,
    )

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

    group_general.add_argument( '--depslock-path',
        metavar='FILE',
        default=pm_common.CMAKEPM_DEPENDENCYLOCK_FILENAME,
        help='path to file with locked dependencies (default: ./%(default)s)'
    )

    group_output = parser.add_argument_group( 'output arguments' )

    group_output.add_argument( '--out-format',
        metavar='TYPE',
        choices=pm_download_output.get_output_types(),
        default='stdout',
        help='output data format. Avalible format types:[%(choices)s] (default: %(default)s)',
    )
    group_output.add_argument( '-o', '--output',
        metavar='FILE',
        help='output file name (required if --out_format is not stdout)',
    )
    group_output.add_argument( '--out-prefix',
        metavar='PREFIX',
        default='',
        help='prefix for output variable name (default: no prefix at all)',
    )


def make_parser_promote( subparsers ):

    parser = subparsers.add_parser( 'promote',
        help='a promote help',
    )

    parser.set_defaults(
        check_args=check_args_cmd_promote,
        call_cmd=cmd_promote,
    )

    group_general = parser.add_argument_group( 'general arguments' )

    group_general.add_argument( '-c', '--config',
        metavar='FILE',
        help='path to configuration file',
    )


def make_parser_pack( subparsers ):

    parser = subparsers.add_parser( 'pack',
        help='a pack help',
    )

    parser.set_defaults(
        check_args=check_args_cmd_pack,
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

    if not all( (args.osname, args.arch, args.compiler, )):

        pm_common.warning( '\nError: not enought arguments\n')
        parser.print_usage()
        sys.exit( pm_common.CMAKEPM_ERRORCODE_WRONGARGS )


    if 'stdout' == args.out_format:

        if args.output:

            pm_common.warning( "\nError: no need argument '-o|--output' when argument '--out-format={}'\n".format( args.out_format ))
            parser.print_usage()
            sys.exit( pm_common.CMAKEPM_ERRORCODE_WRONGARGS )

    elif not args.output:

        pm_common.warning( "\nError: argument '-o|--output' required when argument '--out-format={}'\n".format( args.out_format ))
        parser.print_usage()
        sys.exit( pm_common.CMAKEPM_ERRORCODE_WRONGARGS )


def check_args_cmd_promote(args):

    pass


def check_args_cmd_pack(args):

    pass


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


def main():

    parser = make_parser()
    args   = parser.parse_args()

    if not vars( args ):
        # no args were passed
        parser.print_help()
        sys.exit( pm_common.CMAKEPM_ERRORCODE_WRONGARGS )

    args.check_args( args )
    args.call_cmd( args )


if __name__ == '__main__':
    main()
