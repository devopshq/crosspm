#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import collections

try:
    import argparse
except:
    # possible we are under python 3.1
    import optparse


# third-party
import requests

from helpers.pm_common import *
from helpers import pm_download_output

OPT_ARG_PARSER  = 'argparse' in locals()
OPT_ARGS        = None

def download_package(from_url, save_path, out_error_list):

    warning( 'DEPRECATED function pm_arti_download.py:download_package()' )

    default_source = OPT_SOURCES[ 0 ]
        
    result = __download_package(
        default_source[ 'auth' ],
        from_url,
        save_path,
        out_error_list,
    )

    return result

def __download_package(auth, package_url, save_path, out_error_list):

    chunk_size  = 1024
    result      = False
    
    try:    
        
        r = requests.get(
            package_url,
            verify=False,
            auth=auth,
            stream=True,        # support huge file size
        )

        r.raise_for_status()

        if not os.path.exists( os.path.dirname( save_path ) ):
            
            os.makedirs( os.path.dirname( save_path ))

        # download file
        with open( save_path, 'wb+' ) as fd:
            
            for chunk in r.iter_content( chunk_size ):
                
                if chunk: # filter out keep-alive new chunks
                    
                    fd.write( chunk )
                    fd.flush()

        r.close()
        
        result = True

    except Exception as e:
        
        out_error_list.append( repr( e ) )
        
        
    return result


def package_exists(auth, package_url, out_error_list):

    package_found = False
    error_occured = False

    try:    
        r = requests.get(
            package_url,
            verify=False,
            auth=auth,
        )

        r.raise_for_status()

        r.close()
        
        package_found = True

    except requests.exceptions.HTTPError as e:

        if 404 != e.response.status_code:
            
            error_occured = True
            out_error_list.append( repr( e ) )


    except Exception as e:
        
        error_occured = True
        out_error_list.append( repr( e ) )
        
        
    return ( package_found, error_occured, )


def join_package_path(server_url, repo, path):

    server_url  = server_url  if not server_url.endswith( '/' )  else server_url[ : -1 ]
    repo        = repo        if not repo.startswith( '/' )      else repo[ 1 : ]
    repo        = repo        if not repo.endswith( '/' )        else repo[ : -1 ]
    path        = path        if not path.startswith( '/' )      else path[ 1 : ]

    return '{}/{}/{}'.format( server_url, repo, path )


def print_deps_tree(deps_tree):
    
    def __print_deps_tree(deps_tree, nodes=None):
        
        nodes = [] if nodes is None else nodes
        
        n = len( deps_tree )
        for i, (k, v) in enumerate( deps_tree.items() ):
            
            left_side = ''
            for item in nodes:
                left_side += '    |' if item else '     '
            
            warning( left_side + '    |' )
            warning( '{}    +--{}'.format(
                left_side,
                k,
            ))
    
            if v:
                nodes.append( 1 if i < n-1 else 0 )
                __print_deps_tree( v, nodes )
                nodes.pop()
    
    warning( '\nROOT+' )
    __print_deps_tree( deps_tree )
    warning( '\n' + '='*80 )
        
    
def make_deps_tree(package_list):
    
    package_list = sorted( package_list, key=lambda x: x[2] )
    
    result = collections.OrderedDict()
    
    for ( root_package, package, package_name, extracted_package, ) in package_list:

        leaves  = root_package + [ package_name ]
        it      = result.setdefault( leaves[ 0 ], collections.OrderedDict() )
        
        for item in leaves[ 1 :  ]:
        
            it = it.setdefault( item, collections.OrderedDict() )
            
    return result


def check_dependencies(package_list, unique_package_list=None):

    unique_package_list = [] if unique_package_list is None else unique_package_list
    unique_package_dict = {}
    errors              = {}
    
    for item in package_list:

        (
            root_package,
            package,
            package_name,
            extracted_package,
        ) = item
        
        if package not in unique_package_dict:
        
            unique_package_dict[ package ] = package_name
            unique_package_list.append( item )
            
        elif unique_package_dict[ package ] != package_name:
        
                current_packege_name = unique_package_dict[ package ]
                errors.setdefault( package, [ current_packege_name ] ).append( package_name )
        
    for package, package_names in errors.items():
        
        warning( 'ERROR: Project link multiple versions of package {}:'.format( package ) )
        
        for package_name in package_names:
            warning( '    {}'.format( package_name ) )
        
    return not len( errors )
    
    
            
def get_packages():

    warning( 'Reading {} ...'.format( CMAKEPM_DEPENDENCYLOCK_FILENAME ) )
    
    package_list = []
    __get_packages( OPT_ARGS.osname, OPT_ARGS.arch, OPT_ARGS.compiler, os.getcwd(), [], package_list )
    
    warning( 'Check dependencies ...' )
    
    package_deps_tree = make_deps_tree( package_list )
        
    print_deps_tree( package_deps_tree )
    
    unique_package_list = []
    if not check_dependencies( package_list, unique_package_list ):
        warning("Error: aborting due to previous error")
        sys.exit( CMAKEPM_ERRORCODE_MULTIPLE_DEPS )
    
    unique_package_list = sorted( unique_package_list, key=lambda x: x[2] )
    
    pm_download_output.make_output(
        OPT_ARGS.out_format,
        OPT_ARGS.output,
        OPT_ARGS.out_prefix,
        unique_package_list
    )
        
    warning( 'Done!' )


def __get_packages(osname, arch, compiler, current_path, root_package, result):
    
    packages = getDependencies( os.path.join( current_path, CMAKEPM_DEPENDENCYLOCK_FILENAME ) )
    root     = get_cmakepm_root()

    root_packages = os.path.join(root, 'cache')
    root_archives = os.path.join(root, 'archive')
    
    for package, version_tuple, branch in packages:
        
        compiler_old            = 'gcc'     if compiler.startswith( 'gcc' ) else compiler
        osname_old              = 'linux'   if compiler.startswith( 'gcc' ) else 'win'
        
        version                 = '.'.join( map(str, version_tuple) )
        package_name            = '{} {} {}'.format( package, version, branch )
        lib_rel_path            = '{package}/{branch}/{version}/{compiler}/{arch}/{osname}'.format(**locals())
        package_url             = '{lib_rel_path}/{package}.{version}.tar.gz'.format(**locals())
        package_url_old         = '{package}/{branch}/{version}/{compiler_old}/{arch}/{osname_old}/{package}.{version}-{branch}-{compiler_old}.zip'.format(**locals())
        archived_package        = '{root_archives}/{package}-{branch}.{version}-{compiler}{arch}-{osname}.tar.gz'.format(**locals())
        archived_package_tmp    = '{archived_package}_tmp'.format(**locals())
        extracted_package       = '{root_packages}/{lib_rel_path}'.format(**locals())
        extracted_package       = extracted_package.replace( '\\', '/' )
        
        result.append( [
            list( root_package ),
            package,
            package_name,
            extracted_package,
        ])
        
        warning( 'Search package [{package}] ...'.format(**locals()) )
        
        # download package
        if not os.path.exists( archived_package ):
        
            # remove temp file
            if os.path.exists( archived_package_tmp ):
                os.remove( archived_package_tmp )

            error_str           = []
            search_package_urls = []
            found_package_url   = None
            
            for current_source in OPT_SOURCES:

                for current_repo in current_source[ 'repos' ]:

                    search_package_urls.append((
                        current_source[ 'auth' ],
                        join_package_path(
                            current_source[ 'server_url' ],
                            current_repo,
                            package_url,
                        ),
                    ))

                    search_package_urls.append((
                        current_source[ 'auth' ],
                        join_package_path(
                            current_source[ 'server_url' ],
                            current_repo,
                            package_url_old,
                        ),
                    ))

            for current_package_url in search_package_urls:                    

                package_found, error_occured = package_exists(
                    current_package_url[ 0 ],
                    current_package_url[ 1 ],
                    error_str,
                )

                if package_found:

                    found_package_url = current_package_url
                    break

                elif error_occured:

                    warning( 'FAILED to search package {} at url: [{}]\n'.format( package_name, found_package_url[ 1 ] ))
                    warning( '    with message {}\n'.format( error_str[ 0 ] ))
                    sys.exit( CMAKEPM_ERRORCODE_SERVER_CONNECT_ERROR )

            else:

                warning( 'FAILED to download package {}\n    next path was checked:\n'.format( package_name ))

                for item in search_package_urls:
                    warning( '    [{}]\n'.format( item[ 1 ] ))
                
                sys.exit( CMAKEPM_ERRORCODE_PACKAGE_NOT_FOUND )
            

            warning( 'Downloading ...' )

            package_downloaded = __download_package(
                current_package_url[ 0 ],
                current_package_url[ 1 ],
                archived_package_tmp,
                error_str,
            )

            if not package_downloaded:
            
                warning( 'FAILED to download {}\n'.format( package_name ))
                warning( '    with message {}\n'.format( error_str[ 0 ] ))
                sys.exit( CMAKEPM_ERRORCODE_SERVER_CONNECT_ERROR )
                
            os.renames( archived_package_tmp, archived_package )

            
        # extract package
        if not os.path.exists( extracted_package ):
            
            warning( 'Extracting archive ...' )
            extractArchive( archived_package, extracted_package )
        
        # recursive download dependencies
        if( os.path.exists( os.path.join( extracted_package, CMAKEPM_DEPENDENCYLOCK_FILENAME ) ) ):
            warning( 'Search dependencies for package [{package}] ...'.format(**locals()) )
            
            root_package.append( package_name )
            __get_packages( osname, arch, compiler, extracted_package, root_package, result )
            root_package.pop()
            
            warning( 'Dependencies for package [{package}] done!'.format(**locals()) )
        
def make_arg_parser():
    
    parser = argparse.ArgumentParser()
    
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

    return parser
    
def make_opt_parser():
    
    usage = '''usage: %prog [-h] [-c FILE] [-o FILE]
                           [--out-format TYPE]
                           [--out-prefix PREFIX]
                           <OS> <ARCH> <CL>

positional arguments:
  <OS>                  target operation system name
  <ARCH>                target build architecture type
  <CL>                  current compiler name
'''
    
    parser = optparse.OptionParser( usage=usage )

    group_general = optparse.OptionGroup( parser, 'general arguments' )

    group_output.add_option( '-c', '--config',
        metavar='FILE',
        help='path to configuration file',
    )
                 
    group_output = optparse.OptionGroup( parser, 'output arguments' )
                    
    group_output.add_option( '--out-format',
        metavar='TYPE',
        type='choice',
        choices=pm_download_output.get_output_types(),
        default='stdout',
        help='output data format. Avalible format types:{} (default: stdout)'.format(
            pm_download_output.get_output_types()
        ),
    )
    group_output.add_option( '-o', '--output',
        metavar='FILE',
        help='output file name (required if --out_format is not stdout)',
    )
    group_output.add_option( '--out-prefix',
        metavar='PREFIX',
        default='',
        help='prefix for output variable name (default: no prefix at all)',
    )
    
    parser.add_option_group( group_output )
    
    return parser
    
def parse_args():

    global OPT_ARGS
    
    parser = None
    
    if OPT_ARG_PARSER:
        parser          = make_arg_parser()
        OPT_ARGS        = OptDict( parser.parse_args() )
        
    else:
        parser          = make_opt_parser()
        (options, args) = parser.parse_args()
        OPT_ARGS        = OptDict(
            options,
            optparse=True,
            optparse_args=args,
            optparse_args_names=( 'osname', 'arch', 'compiler', ),
        )
        
    if not all( (OPT_ARGS.osname, OPT_ARGS.arch, OPT_ARGS.compiler, )):
        
        warning( '\nError: not enought arguments\n')
        parser.print_usage()
        sys.exit( CMAKEPM_ERRORCODE_WRONGARGS )
    
    
    if 'stdout' == OPT_ARGS.out_format:
        
        if OPT_ARGS.output:
        
            warning( "\nError: no need argument '-o|--output' when argument '--out-format={}'\n".format( OPT_ARGS.out_format ))
            parser.print_usage()
            sys.exit( CMAKEPM_ERRORCODE_WRONGARGS )
        
    elif not OPT_ARGS.output:
    
        warning( "\nError: argument '-o|--output' required when argument '--out-format={}'\n".format( OPT_ARGS.out_format ))
        parser.print_usage()
        sys.exit( CMAKEPM_ERRORCODE_WRONGARGS )

    
def main():

    parse_args()
    load_config( OPT_ARGS.config )
    get_packages()

    
if __name__ == '__main__':
    main()
