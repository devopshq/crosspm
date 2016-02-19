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
import os
import collections

from crosspm.helpers import pm_common
from crosspm.helpers import pm_download_output

# third-party
import requests


class CrosspmDownloader:

    def __init__(self, options_dict):

        self.__config            = None
        self.__option_osname     = options_dict[ 'osname'     ]
        self.__option_arch       = options_dict[ 'arch'       ]
        self.__option_compiler   = options_dict[ 'compiler'   ]
        self.__option_out_format = options_dict[ 'out_format' ]
        self.__option_output     = options_dict[ 'output'     ]
        self.__option_out_prefix = options_dict[ 'out_prefix' ]

    def set_config(self, data):

        self.__config = pm_common.parse_config( data )

    def set_config_from_file(self, filepath=None):

        data = pm_common.read_config( filepath )
        self.set_config( data )

    def download_package(self, auth, package_url, save_path, out_error_list):

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


    def package_exists(self, auth, package_url, out_error_list):

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


    def join_package_path(self, server_url, repo, path):

        server_url  = server_url  if not server_url.endswith( '/' )  else server_url[ : -1 ]
        repo        = repo        if not repo.startswith( '/' )      else repo[ 1 : ]
        repo        = repo        if not repo.endswith( '/' )        else repo[ : -1 ]
        path        = path        if not path.startswith( '/' )      else path[ 1 : ]

        return '{}/{}/{}'.format( server_url, repo, path )


    def print_deps_tree(self, deps_tree):

        def print_deps_tree_inner(deps_tree, nodes=None):

            nodes = [] if nodes is None else nodes

            n = len( deps_tree )
            for i, (k, v) in enumerate( deps_tree.items() ):

                left_side = ''
                for item in nodes:
                    left_side += '    |' if item else '     '

                pm_common.warning( left_side + '    |' )
                pm_common.warning( '{}    +--{}'.format(
                    left_side,
                    k,
                ))

                if v:
                    nodes.append( 1 if i < n-1 else 0 )
                    print_deps_tree_inner( v, nodes )
                    nodes.pop()

        pm_common.warning( '\nROOT+' )
        print_deps_tree_inner( deps_tree )
        pm_common.warning( '\n' + '='*80 )


    def make_deps_tree(self, package_list):

        package_list = sorted( package_list, key=lambda x: x[2] )

        result = collections.OrderedDict()

        for ( root_package, package, package_name, extracted_package, ) in package_list:

            leaves  = root_package + [ package_name ]
            it      = result.setdefault( leaves[ 0 ], collections.OrderedDict() )

            for item in leaves[ 1 :  ]:

                it = it.setdefault( item, collections.OrderedDict() )

        return result


    def check_dependencies(self, package_list, unique_package_list=None):

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

            pm_common.warning( 'ERROR: Project link multiple versions of package [{}]:'.format( package ) )

            for package_name in package_names:
                pm_common.warning( '    {}'.format( package_name ) )

        return not len( errors )



    def get_packages(self):

        pm_common.warning( 'Reading {} ...'.format( pm_common.CMAKEPM_DEPENDENCYLOCK_FILENAME ) )

        package_list = []
        self.get_packages_inner( self.__option_osname, self.__option_arch, self.__option_compiler, os.getcwd(), [], package_list )

        pm_common.warning( 'Check dependencies ...' )

        package_deps_tree = self.make_deps_tree( package_list )

        self.print_deps_tree( package_deps_tree )

        unique_package_list = []
        if not self.check_dependencies( package_list, unique_package_list ):
            pm_common.warning("Error: aborting due to previous error")
            sys.exit( pm_common.CMAKEPM_ERRORCODE_MULTIPLE_DEPS )

        unique_package_list = sorted( unique_package_list, key=lambda x: x[2] )

        pm_download_output.make_output(
            self.__option_out_format,
            self.__option_output,
            self.__option_out_prefix,
            unique_package_list
        )

        pm_common.warning( 'Done!' )


    def get_packages_inner(self, osname, arch, compiler, current_path, root_package, result):

        packages = pm_common.getDependencies( os.path.join( current_path, pm_common.CMAKEPM_DEPENDENCYLOCK_FILENAME ) )
        root     = pm_common.get_cmakepm_root()

        root_packages = os.path.join(root, 'cache')
        root_archives = os.path.join(root, 'archive')

        avalible_options = [
            (
                osname,   # osname
                'any',    # arch
                'any',    # compiler
            ),
            (
                osname,   # osname
                arch,     # arch
                'any',    # compiler
            ),
            (
                osname,   # osname
                'any',    # arch
                compiler, # compiler
            ),
            (
                osname,   # osname
                arch,     # arch
                compiler, # compiler
            ),
        ]

        for ( package, version_tuple, branch ) in packages:

            checked_package_urls = []
            package_params_list  = []

            for current_source in self.__config[ 'sources' ]:

                for current_repo in current_source[ 'repos' ]:

                    for ( current_osname, current_arch, current_compiler ) in avalible_options:

                        package_params_list.append((
                            current_source,
                            current_repo,
                            current_osname,
                            current_arch,
                            current_compiler,
                        ))


            pm_common.warning( 'Search package [{package}] ...'.format(**locals()) )

            for ( current_source, current_repo, curr_osname, curr_arch, curr_compiler ) in package_params_list:

                version                   = '.'.join( map(str, version_tuple) )
                package_name              = '{} {} {}'.format( package, version, branch )
                lib_rel_path              = '{package}/{branch}/{version}/{curr_compiler}/{curr_arch}/{curr_osname}'.format(**locals())
                archived_package          = '{root_archives}/{package}-{branch}.{version}-{curr_compiler}{curr_arch}-{curr_osname}.tar.gz'.format(**locals())
                archived_package_tmp      = '{archived_package}_tmp'.format(**locals())
                extracted_package         = '{root_packages}/{lib_rel_path}'.format(**locals())
                extracted_package         = extracted_package.replace( '\\', '/' )
                package_short_url         = '{lib_rel_path}/{package}.{version}.tar.gz'.format(**locals())
                package_full_url          = self.join_package_path( current_source[ 'server_url' ], current_repo, package_short_url )

                # download package
                if not os.path.exists( archived_package ):

                    # remove temp file
                    if os.path.exists( archived_package_tmp ):
                        os.remove( archived_package_tmp )

                    error_str                    = []
                    package_found, error_occured = self.package_exists(
                        current_source[ 'auth' ],
                        package_full_url,
                        error_str,
                    )

                    if error_occured:

                        pm_common.warning( 'FAILED to search package {} at url: [{}]\n'.format( package_name, package_full_url ))
                        pm_common.warning( '    with message {}\n'.format( error_str[ 0 ] ))
                        sys.exit( pm_common.CMAKEPM_ERRORCODE_SERVER_CONNECT_ERROR )

                    if not package_found:

                        checked_package_urls.append( package_full_url )
                        continue

                    pm_common.warning( 'Downloading ...' )

                    package_downloaded = self.download_package(
                        current_source[ 'auth' ],
                        package_full_url,
                        archived_package_tmp,
                        error_str,
                    )

                    if not package_downloaded:

                        pm_common.warning( 'FAILED to download {}\n'.format( package_name ))
                        pm_common.warning( '    with message {}\n'.format( error_str[ 0 ] ))
                        sys.exit( pm_common.CMAKEPM_ERRORCODE_SERVER_CONNECT_ERROR )

                    os.renames( archived_package_tmp, archived_package )


                # extract package
                if not os.path.exists( extracted_package ):

                    pm_common.warning( 'Extracting archive ...' )
                    pm_common.extractArchive( archived_package, extracted_package )


                result.append( [
                    list( root_package ),
                    package,
                    package_name,
                    extracted_package,
                ])

                # recursive download dependencies
                if( os.path.exists( os.path.join( extracted_package, pm_common.CMAKEPM_DEPENDENCYLOCK_FILENAME ) ) ):
                    pm_common.warning( 'Search dependencies for package [{package}] ...'.format(**locals()) )

                    root_package.append( package_name )
                    self.get_packages_inner( osname, arch, compiler, extracted_package, root_package, result )
                    root_package.pop()

                    pm_common.warning( 'Dependencies for package [{package}] done!'.format(**locals()) )



                break

            else:
                pm_common.warning( 'FAILED to download package {}\n    next path was checked:\n'.format( package_name ))

                for item in checked_package_urls:
                    pm_common.warning( '    [{}]\n'.format( item ))

                sys.exit( pm_common.CMAKEPM_ERRORCODE_PACKAGE_NOT_FOUND )


class CrosspmPromoter:

    def __init__(self):

        self.__config = None

    def set_config(self, data):

        self.__config = pm_common.parse_config( data )

    def set_config_from_file(self, filepath=None):

        data = pm_common.read_config( filepath )
        self.set_config( data )


    def get_version_int(self, version_str):

        parts = version_str.split( '.' )
        try:
            if len( parts ) < 4:
                return (int(parts[0]), int(parts[1]), 0, int(parts[2]))

            return (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
        except ValueError:
            return (0, 0, 0, 0)
        except IndexError:
            return (0, 0, 0, 0)


    def parse_dirlist(self, data_dict, dirlist_data):

        for item in dirlist_data[ "files" ]:

            if item[ "folder" ]:
                continue

            parts = item[ "uri" ].split( '/' )

            name        = parts[ 1 ]
            branch      = parts[ 2 ]
            version     = parts[ 3 ]
            version_int = self.get_version_int( version )

            data_dict.setdefault( name, {} )
            data_dict[ name ].setdefault( branch, [] )
            data_dict[ name ][ branch ].append( ( version, version_int ))


    def join_package_path(self, server_url, part_a, repo, path):

        server_url  = server_url  if not server_url.endswith( '/' )  else server_url[ : -1 ]
        part_a      = part_a      if not part_a.startswith( '/' )    else part_a[ 1 : ]
        part_a      = part_a      if not part_a.endswith( '/' )      else part_a[ : -1 ]
        repo        = repo        if not repo.startswith( '/' )      else repo[ 1 : ]
        repo        = repo        if not repo.endswith( '/' )        else repo[ : -1 ]
        path        = path        if not path.startswith( '/' )      else path[ 1 : ]

        return '{server_url}/{part_a}/{repo}/{path}'.format( **locals() )


    def promote_packages(self):

        data_tree         = {}
        deps_list         = pm_common.getDependencies( os.path.join( os.getcwd(), pm_common.CMAKEPM_DEPENDENCY_FILENAME ) )
        out_file_data_str = ''
        out_file_format   = '{:20s} {:20s} {}\n'
        out_file_path     = os.path.join( os.getcwd(), pm_common.CMAKEPM_DEPENDENCYLOCK_FILENAME )



        # clean file
        with open( out_file_path, 'w' ) as out_f:

            out_f.write( out_file_format.format( '# package', '# version', '# branch\n' ))


        for current_source in self.__config[ 'sources' ]:

            for current_repo in current_source[ 'repos' ]:

                request_url = self.join_package_path(
                    current_source[ 'server_url' ],
                    'api/storage',
                    current_repo,
                    '?list&deep=1&listFolders=0&mdTimestamps=1&includeRootPath=1',
                )

                print( 'get request: {}'.format( request_url ))

                r = requests.get(
                    request_url,
                    verify=False,
                    auth=current_source[ 'auth' ],
                )

                r.raise_for_status()

                data_responce = r.json()

                self.parse_dirlist( data_tree, data_responce )


        for (d_name, d_version, d_branch,) in deps_list:

            if d_name not in data_tree:

                pm_common.warning( 'Error: unknown package [{}]'.format( d_name ))

                sys.exit( pm_common.CMAKEPM_ERRORCODE_PACKAGE_NOT_FOUND )

            if d_branch not in data_tree[ d_name ]:

                pm_common.warning( 'Error: unknown branch [{}] of package [{}]'.format( d_branch, d_name ))

                sys.exit( pm_common.CMAKEPM_ERRORCODE_PACKAGE_BRANCH_NOT_FOUND )

            libs = data_tree[ d_name ][ d_branch ]


            def version_filter_fn( v ):

                lambda_f = lambda pair: pair[0] == '*' or int(pair[0]) == pair[1]

                return all( map( lambda_f, zip( d_version, v[ 1 ] )))


            versions = list( filter( version_filter_fn, libs ))

            if not versions:

                pm_common.warning( 'Error: pattern [{ver}] does not match any version of package [{pkg}] for branch [{br}] '.format(
                    ver='.'.join( d_version ),
                    pkg=d_name,
                    br=d_branch,
                ))

                sys.exit( pm_common.CMAKEPM_ERRORCODE_VERSION_PATTERN_NOT_MATCH )

            current_version = max( versions, key=lambda x: x[ 1 ] )


            out_file_data_str += out_file_format.format(
                d_name,
                current_version[ 0 ],
                d_branch
            )

        with open( out_file_path, 'w' ) as out_f:

            out_f.write( out_file_data_str )
