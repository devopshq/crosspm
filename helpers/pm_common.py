# -*- coding: utf-8 -*-

from __future__ import print_function # support for print to stderr from Python 2.7

import os
import sys
import tarfile
import zipfile
import contextlib
import shutil
import json

from requests.packages.urllib3 import disable_warnings
disable_warnings()


CMAKEPM_DEPENDENCY_FILENAME      = 'dependencies.txt'
CMAKEPM_DEPENDENCYLOCK_FILENAME  = '{}.lock'.format(CMAKEPM_DEPENDENCY_FILENAME)
CMAKEPM_CONFIG_DEFAULT_FILENAME  = 'cmakepm.config'

CMAKEPM_ERRORCODES = (
    CMAKEPM_ERRORCODE_SUCCESS,
    CMAKEPM_ERRORCODE_FILEDEPSNOTFOUND,
    CMAKEPM_ERRORCODE_WRONGSYNTAX,
    CMAKEPM_ERRORCODE_MULTIPLE_DEPS,
    CMAKEPM_ERRORCODE_NO_FILES_TO_PACK,
    CMAKEPM_ERRORCODE_SERVER_CONNECT_ERROR,
    CMAKEPM_ERRORCODE_PACKAGE_NOT_FOUND,
    CMAKEPM_ERRORCODE_PACKAGE_BRANCH_NOT_FOUND,
    CMAKEPM_ERRORCODE_VERSION_PATTERN_NOT_MATCH,
    CMAKEPM_ERRORCODE_UNKNOWN_OUTTYPE,
    CMAKEPM_ERRORCODE_FILE_IO,
    CMAKEPM_ERRORCODE_WRONGARGS,
    CMAKEPM_ERRORCODE_CONFIG_NOT_DEFINED,
    CMAKEPM_ERRORCODE_CONFIG_NOT_EXIST,
    CMAKEPM_ERRORCODE_CONFIG_IO_ERROR,
) = range( 15 )

OPT_SOURCES = []


def warning(*args, **kwargs):

    kwargs.update( {'file': sys.stderr} )

    print( *args, **kwargs )

def get_cmakepm_root():

    root = os.getenv( 'CMAKEPM_CACHE_ROOT' )

    if not root:
        
        home_dir = os.getenv( 'APPDATA' )  if os.name == 'nt'  else os.getenv( 'HOME' )

        root     = os.path.join( home_dir, '.cmakepm' )

    return root

def getPackageParams(i, line):

    name    = ''
    version = ''
    branch  = ''

    parts   = line.split()
    n       = len( parts )

    if n not in (2, 3,):
        warning( 'Error: wrong syntax at line {}. File: [{}]'.format( i, filepath ) )
        sys.exit( CMAKEPM_ERRORCODE_WRONGSYNTAX )

    if parts[ 1 ] == '*':
        parts[ 1 ] = '*.*.*.*'

    name    = parts[ 0 ]
    version = tuple( parts[ 1 ].split( '.' ) )
    branch  = parts[ 2 ] if n == 3 else 'master'

    return ( name, version, branch, )


def getDependencies(filepath):

    result = []

    if not os.path.exists( filepath ):
        warning( 'Error: file not found: [{}]'.format( filepath ) )
        sys.exit( CMAKEPM_ERRORCODE_FILEDEPSNOTFOUND )

    with open(filepath, 'r') as f:
        for i, line in enumerate(f):

            line = line.strip()

            if not line or line.startswith( '#' ):
                continue

            result.append( getPackageParams( i, line ) )

        return result

def createArchive(archive_name, src_dir_path):

    archive_name        = os.path.realpath( archive_name )
    src_dir_path        = os.path.realpath( src_dir_path )
    files_to_pack       = []
    archive_name_tmp    = os.path.join(
        os.path.dirname( archive_name ),
        'tmp_{}'.format( os.path.basename( archive_name )),
    )

    for name in os.listdir( src_dir_path ):

        current_path    = os.path.join( src_dir_path, name )
        real_path       = os.path.realpath( current_path )
        rel_path        = os.path.relpath( current_path, src_dir_path )

        files_to_pack.append( ( real_path, rel_path, ))

    if not files_to_pack:
        warning( 'Error: no files to pack, directory [{}] is empty'.format( src_dir_path ) )
        sys.exit( CMAKEPM_ERRORCODE_NO_FILES_TO_PACK )



    with contextlib.closing( tarfile.TarFile.open( archive_name_tmp, 'w:gz' )) as tf:

        for real_path, rel_path in files_to_pack:

            tf.add( real_path, arcname=rel_path )

    os.renames( archive_name_tmp, archive_name )

def extractArchive(archive_name, dst_dir_path):

    dst_dir_path_tmp = '{}_tmp'.format( dst_dir_path )

    # remove temp dir
    if os.path.exists( dst_dir_path_tmp ):
        shutil.rmtree( dst_dir_path_tmp )

    if tarfile.is_tarfile( archive_name ):

        with contextlib.closing( tarfile.TarFile.open( archive_name, 'r:*' )) as tf:
            tf.extractall( path=dst_dir_path_tmp )

    elif zipfile.is_zipfile( archive_name ):

        with contextlib.closing( zipfile.ZipFile( archive_name, mode='r' )) as zf:
            zf.extractall( path=dst_dir_path_tmp )

    else:
        warning( 'Error: unknown archive type. File: [{}]'.format( archive_name ))

    os.renames( dst_dir_path_tmp, dst_dir_path )

# order of priority:
# - option "--config" passed to script or argument filepath of api call
# - enviroment variable "CMAKEPM_CONFIG_PATH"
# - file "cmakepm.config" located at working dir
# - file "cmakepm.config" located at cmakepm source dir

def read_config(filepath=None):

    result = {}

    if filepath is None:

        env_config_path     = os.getenv( 'CMAKEPM_CONFIG_PATH' )
        local_config_path   = os.path.join( os.getcwd(), CMAKEPM_CONFIG_DEFAULT_FILENAME )
        default_config_path = os.path.join( os.path.dirname( os.path.realpath( __file__ )), '..', CMAKEPM_CONFIG_DEFAULT_FILENAME )

        config_path_list    = [
                env_config_path,
                local_config_path,
                default_config_path,
        ]

        if env_config_path is not None:
            
            filepath = env_config_path

        elif os.path.exists( local_config_path ):

            filepath = local_config_path

        elif os.path.exists( default_config_path ):

            filepath = default_config_path

        else:

            warning( 'Error: config file not defined. Checked paths: \n\t[{}]\n\t[{}]'.format(
                local_config_path,
                default_config_path,
            ))
            sys.exit( CMAKEPM_ERRORCODE_CONFIG_NOT_DEFINED )

    
    filepath = os.path.realpath( filepath )

    if not os.path.exists( filepath ):
        
        warning( 'Error: config file not found at given path: [{}]'.format( filepath ))
        sys.exit( CMAKEPM_ERRORCODE_CONFIG_NOT_EXIST )

    warning( 'Reading config file... [{}]'.format( filepath ))

    try:
        
        f      = open( filepath )
        result = json.loads( f.read() )
        f.close()

        

    except Exception as e:

        warning( 'Error: catch exception while reading config file: [{}]\n\tException type: {}\n\tMessage: {}'.format(
            filepath,
            type( e ),
            repr( e ),
        ))
        sys.exit( CMAKEPM_ERRORCODE_CONFIG_IO_ERROR )


    return result

def parse_config(data):

    result = {
        'sources': [],
    }

    for item_str in data[ 'sources' ]:
        
        item_list = item_str.split()

        result[ 'sources' ].append({
            'connector_type': item_list[ 0 ],
            'server_url':     item_list[ 1 ],
            'repos':          [ x.strip() for x in item_list[ 2 ].split( ',' ) ],
            'auth_type':      item_list[ 3 ],
            'auth':           ( item_list[ 4 ], item_list[ 5 ], ),
        })

    return result

def load_config(filepath=None):

    config_data = read_config( filepath )
    config_dict = parse_config( config_data )

    OPT_SOURCES.extend( config_dict[ 'sources' ] )
    