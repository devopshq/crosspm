#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

import api
from helpers import pm_common
from helpers import pm_download_output

def make_parser():

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='PROG')
    
    #parser.add_argument('--foo', action='store_true', help='foo help')
    subparsers = parser.add_subparsers(help='sub-command help')
    
    # create the parser for the "a" command
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
        'osname':     args.osname,
        'arch':       args.arch,
        'compiler':   args.compiler,
        'out_format': args.out_format,
        'output':     args.output,
        'out_prefix': args.out_prefix,
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

    args.check_args( args )
    args.call_cmd( args )

    
if __name__ == '__main__':
    main()
