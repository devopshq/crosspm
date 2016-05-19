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


import os
import re

from crosspm.helpers import pm_common


log = logging.getLogger( __name__ )


def _output_type_stdout(out_format, out_filepath, out_prefix, packages):

    for ( root_package, package, package_name, extracted_package, ) in packages:

        print( '{out_prefix}{package}: {extracted_package}'.format( **locals() ))


def _output_type_shell(out_format, out_filepath, out_prefix, packages):

    result = '\n'

    for ( root_package, package, package_name, extracted_package, ) in packages:

        curr_var_name   = _get_var_name( out_prefix, package )
        result          += "{curr_var_name}='{extracted_package}'\n".format( **locals() )

    result += '\n'

    _write_to_file( result, out_filepath )

    log.info(
        'Write packages info to file [%s]\n\tcontent:\n\t%s',
        out_filepath,
        result,
    )

def _output_type_cmd(out_format, out_filepath, out_prefix, packages):

    result = '\n'

    for ( root_package, package, package_name, extracted_package, ) in packages:

        curr_var_name   = _get_var_name( out_prefix, package )
        result          += 'set {curr_var_name}={extracted_package}\n'.format( **locals() )

    result += '\n'

    _write_to_file( result, out_filepath )

    log.info(
        'Write packages info to file [%s]\n\tcontent:\n\t%s',
        out_filepath,
        result,
    )

def _output_type_python(out_format, out_filepath, out_prefix, packages):

    result              = '# -*- coding: utf-8 -*-\n\n'
    packages_dict_str   = ''

    for ( root_package, package, package_name, extracted_package, ) in packages:

        curr_var_name       =  _get_var_name( out_prefix, package )
        result              += "{curr_var_name} = '{extracted_package}'\n".format( **locals() )
        packages_dict_str   += "\t'{curr_var_name}': '{extracted_package}',\n".format( **locals() )

    result += '\nPACKAGES_ROOT = {\n' + packages_dict_str + '}\n'

    _write_to_file( result, out_filepath )

    log.info(
        'Write packages info to file [%s]\n\tcontent:\n\t%s',
        out_filepath,
        result,
    )


def _output_type_json(out_format, out_filepath, out_prefix, packages):

    result  = '{\n'
    n       = len( packages )

    for i, ( root_package, package, package_name, extracted_package, ) in enumerate( packages ):

        curr_var_name   =  _get_var_name( out_prefix, package )
        comma           =  ','  if i < n - 1  else ''
        result          += "\t\"{curr_var_name}\": \"{extracted_package}\"{comma}\n".format( **locals() )

    result += '}\n'

    _write_to_file( result, out_filepath )

    log.info(
        'Write packages info to file [%s]\n\tcontent:%s',
        out_filepath,
        result,
    )


def _get_var_name(out_prefix, package):

    result = '{}{}_ROOT'.format( out_prefix, package )

    result = result.upper()
    result = result.replace( '-', '_' )
    result = re.sub( r'[^A-Z_0-9]', '', result )

    if not result[ 0 ].isalpha()  or '_' == result[ 0 ]:

        result = '_' + result

    return result


def _write_to_file(text, out_filepath):

    out_filepath    = os.path.realpath( out_filepath )
    out_dir_path    = os.path.dirname( out_filepath )

    if not os.path.exists( out_dir_path ):

        log.info( 'mkdirs [%s] ...', out_dir_path )
        os.makedirs( out_dir_path )

    elif not os.path.isdir( out_dir_path ):

        raise pm_common.CrosspmException(
            pm_common.CMAKEPM_ERRORCODE_FILE_IO,
            'Unable to make directory [{}]. File with the same name exists'.format(
                out_dir_path
        ))

    with open( out_filepath, 'w+' ) as f:

        f.write( text )

def get_output_types():

    return list( _OUTPUT_FORMAT_MAP.keys() )


def make_output(out_format, out_filepath, out_prefix, packages):

    if out_format not in _OUTPUT_FORMAT_MAP:
        raise pm_common.CrosspmException(
            pm_common.CMAKEPM_ERRORCODE_UNKNOWN_OUTTYPE,
            'Error: unknown output type: [{}]'.format( out_format ),
        )

    f = _OUTPUT_FORMAT_MAP[ out_format ]

    return f( out_format, out_filepath, out_prefix, packages )


_OUTPUT_FORMAT_MAP = {
    'stdout':   _output_type_stdout,
    'shell':    _output_type_shell,
    'cmd':      _output_type_cmd,
    'python':   _output_type_python,
    'json':     _output_type_json,
}
