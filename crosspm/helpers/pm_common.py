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


from __future__ import print_function # support for print to stderr from Python 2.7

import contextlib
import json
import logging
import os
import shutil
import sys
import tarfile
import zipfile

from requests.packages.urllib3 import disable_warnings
disable_warnings()


log = logging.getLogger( __name__ )

CROSSPM_DEPENDENCY_FILENAME      = 'dependencies.txt'
CROSSPM_DEPENDENCYLOCK_FILENAME  = '{}.lock'.format(CROSSPM_DEPENDENCY_FILENAME)
CROSSPM_CONFIG_DEFAULT_FILENAME  = 'crosspm.config'

CROSSPM_ERRORCODES = (
    CROSSPM_ERRORCODE_SUCCESS,
    CROSSPM_ERRORCODE_UNKNOWN_ERROR,
    CROSSPM_ERRORCODE_WRONGARGS,
    CROSSPM_ERRORCODE_FILEDEPSNOTFOUND,
    CROSSPM_ERRORCODE_WRONGSYNTAX,
    CROSSPM_ERRORCODE_MULTIPLE_DEPS,
    CROSSPM_ERRORCODE_NO_FILES_TO_PACK,
    CROSSPM_ERRORCODE_SERVER_CONNECT_ERROR,
    CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
    CROSSPM_ERRORCODE_PACKAGE_BRANCH_NOT_FOUND,
    CROSSPM_ERRORCODE_VERSION_PATTERN_NOT_MATCH,
    CROSSPM_ERRORCODE_UNKNOWN_OUTTYPE,
    CROSSPM_ERRORCODE_FILE_IO,
    CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
    CROSSPM_ERRORCODE_CONFIG_IO_ERROR,
    CROSSPM_ERRORCODE_UNKNOWN_ARCHIVE,
) = range( 16 )

OPT_SOURCES = []


class CrosspmException(Exception):

    def __init__(self, error_code, msg=''):

        super().__init__( msg )
        self.error_code = error_code
        self.msg = msg


class CrosspmExceptionWrongArgs(CrosspmException):

    def __init__(self, msg=''):

        super().__init__( CROSSPM_ERRORCODE_WRONGARGS, msg )


def print_stderr(*args, **kwargs):

    kwargs.update( {'file': sys.stderr} )

    print( *args, **kwargs )

def get_crosspm_cache_root():

    root = os.getenv( 'CROSSPM_CACHE_ROOT' )

    if not root:

        home_dir = os.getenv( 'APPDATA' )  if os.name == 'nt'  else os.getenv( 'HOME' )
        root     = os.path.join( home_dir, '.crosspm' )

    return root

def getPackageParams(i, line):

    name    = ''
    version = ''
    branch  = ''

    parts   = line.split()
    n       = len( parts )

    if n not in (2, 3,):
        raise CrosspmException(
            CROSSPM_ERRORCODE_WRONGSYNTAX,
            'wrong syntax at line {}. File: [{}]'.format( i, filepath )
        )

    name    = parts[ 0 ]
    version = tuple( parts[ 1 ].split( '.' ) )
    branch  = parts[ 2 ] if n == 3 else 'master'

    return ( name, version, branch, )


def getDependencies(filepath):

    result = []

    if not os.path.exists( filepath ):
        raise CrosspmException(
            CROSSPM_ERRORCODE_FILEDEPSNOTFOUND,
            'file not found: [{}]'.format( filepath ),
        )

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
        raise CrosspmException(
            CROSSPM_ERRORCODE_NO_FILES_TO_PACK,
            'no files to pack, directory [{}] is empty'.format(
                src_dir_path
            ),
        )



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
        raise CrosspmException(
            CROSSPM_ERRORCODE_UNKNOWN_ARCHIVE,
            'unknown archive type. File: [{}]'.format( archive_name ),
        )

    os.renames( dst_dir_path_tmp, dst_dir_path )

def read_config(filepath=None):

    """
    order of priority:
     - option "--config" passed to script or argument filepath of api call
     - enviroment variable "CROSSPM_CONFIG_PATH"
     - file "crosspm.config" located at working dir
    """

    result = {}

    if filepath is None:

        env_var_name    = 'CROSSPM_CONFIG_PATH'
        config_path_env = os.getenv( env_var_name )
        config_path_cwd = os.path.join( os.getcwd(), CROSSPM_CONFIG_DEFAULT_FILENAME )

        if config_path_env:

            log.info( 'Enviroment variable CROSSPM_CONFIG_PATH is set' )
            filepath = config_path_env

        elif os.path.exists( config_path_cwd ):

            log.info( 'Found config file at working directory [%s]', config_path_cwd )
            filepath = config_path_cwd

        else:

            raise CrosspmException(
                CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
                'path to config file is not set',
            )


    filepath = os.path.realpath( filepath )

    if not os.path.exists( filepath ):
        raise CrosspmException(
            CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
            'config file not found at given path: [{}]'.format( filepath )
        )

    log.info( 'Reading config file... [%s]', filepath )

    try:

        with open( filepath ) as f:
            result = json.loads( f.read() )

    except Exception as e:
        log.exception( e )

        code = CROSSPM_ERRORCODE_CONFIG_IO_ERROR
        msg = 'catch exception while reading config file: [{}]'.format(
            filepath,
        )

        raise CrosspmException( code, msg ) from e

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
