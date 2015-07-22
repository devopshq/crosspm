# -*- coding: utf-8 -*-

import sys
import os
import re

from helpers import pm_common

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
    
    pm_common.warning( 'Write packages info to file [{}]\n\tcontent:'.format( out_filepath ))
    pm_common.warning( result )
    
    
def _output_type_cmd(out_format, out_filepath, out_prefix, packages):
    
    result = '\n'
    
    for ( root_package, package, package_name, extracted_package, ) in packages:
        
        curr_var_name   = _get_var_name( out_prefix, package )
        result          += 'set {curr_var_name}={extracted_package}\n'.format( **locals() )
    
    result += '\n'
    
    _write_to_file( result, out_filepath )
    
    pm_common.warning( 'Write packages info to file [{}]\n\tcontent:'.format( out_filepath ))
    pm_common.warning( result )
    
    
def _output_type_python(out_format, out_filepath, out_prefix, packages):
        
    result              = '# -*- coding: utf-8 -*-\n\n'    
    packages_dict_str   = ''
    
    for ( root_package, package, package_name, extracted_package, ) in packages:
        
        curr_var_name       =  _get_var_name( out_prefix, package )
        result              += "{curr_var_name} = '{extracted_package}'\n".format( **locals() )
        packages_dict_str   += "\t'{curr_var_name}': '{extracted_package}',\n".format( **locals() )
    
    result += '\nPACKAGES_ROOT = {\n' + packages_dict_str + '}\n'
    
    _write_to_file( result, out_filepath )
    
    pm_common.warning( 'Write packages info to file [{}]\n\tcontent:'.format( out_filepath ))
    pm_common.warning( result )


def _output_type_json(out_format, out_filepath, out_prefix, packages):
        
    result  = '{\n'
    n       = len( packages )

    for i, ( root_package, package, package_name, extracted_package, ) in enumerate( packages ):
        
        curr_var_name   =  _get_var_name( out_prefix, package )
        comma           =  ','  if i < n - 1  else ''
        result          += "\t\"{curr_var_name}\": \"{extracted_package}\"{comma}\n".format( **locals() )
    
    result += '}\n'
    
    _write_to_file( result, out_filepath )
    
    pm_common.warning( 'Write packages info to file [{}]\n\tcontent:'.format( out_filepath ))
    pm_common.warning( result )


def _get_var_name(out_prefix, package):

    result = '{}{}_ROOT'.format( out_prefix.upper(), package.upper() )

    result = result.replace( '-', '_' )

    # remove unused symbols
    result = re.sub( r'[^a-zA-Z_]', '', result )

    if not result[ 0 ].isalpha()  or '_' == result[ 0 ]:

        result = '_' + result

    return result


def _write_to_file(text, out_filepath):

    out_filepath    = os.path.realpath( out_filepath )    
    out_dir_path    = os.path.dirname( out_filepath )
    
    if not os.path.exists( out_dir_path ):
        
        pm_common.warning(
            'mkdirs [{}] ..'.format( out_dir_path ),
            end='',
        )
        os.makedirs( out_dir_path )
        pm_common.warning( 'Done!' )
        
    elif not os.path.isdir( out_dir_path ):
        
        pm_common.warning( 'Unable to make directory [{}]. File with the same name exists'.format( out_dir_path ))
        sys.exit( pm_common.CMAKEPM_ERRORCODE_FILE_IO )
        
    with open( out_filepath, 'w+' ) as f:
        
        f.write( text )
    
def get_output_types():
    
    return list( _OUTPUT_FORMAT_MAP.keys() )
    
    
def make_output(out_format, out_filepath, out_prefix, packages):
    
    if out_format not in _OUTPUT_FORMAT_MAP:
    
        pm_common.warning( 'Error: unknown output type: [{}]'.format( out_format ))
        sys.exit( pm_common.CMAKEPM_ERRORCODE_UNKNOWN_OUTTYPE )
    
    f = _OUTPUT_FORMAT_MAP[ out_format ]
    
    return f( out_format, out_filepath, out_prefix, packages )
    
    
_OUTPUT_FORMAT_MAP = {
    'stdout':   _output_type_stdout,
    'shell':    _output_type_shell,
    'cmd':      _output_type_cmd,
    'python':   _output_type_python,
    'json':     _output_type_json,
}

