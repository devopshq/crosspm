#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json

# third-party
import requests

from helpers.pm_common import *


def getVersionInt(version_str):
    
    parts = version_str.split( '.' )
    try:
        if len( parts ) < 4:
            return (int(parts[0]), int(parts[1]), 0, int(parts[2]))
            
        return (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
    except ValueError:
        return (0, 0, 0, 0)
    except IndexError:
        return (0, 0, 0, 0)


def make_files_dicts(data):

    result = {}

    for item in data[ "files" ]:

        if item[ "folder" ]:
            continue

        parts = item[ "uri" ].split( '/' )

        name        = parts[ 1 ]
        branch      = parts[ 2 ]
        version     = parts[ 3 ]
        version_int = getVersionInt( version )

        result.setdefault( name, {} )
        result[ name ].setdefault( branch, [] )
        result[ name ][ branch ].append( ( version, version_int ))

    return result


def main():

    deps_list       = getDependencies( os.path.join( os.getcwd(), CMAKEPM_DEPENDENCY_FILENAME ) )

    OPT_PACKAGE_URL = DOMAIN + "/artifactory/api/storage/libs-cpp-release.snapshot?list&deep=1&listFolders=0&mdTimestamps=1&includeRootPath=1"
    request_auth    = ( USER, PASSWORD, )
    
    r = requests.get(
        OPT_PACKAGE_URL,
        verify=False,
        auth=request_auth,
    )

    r.raise_for_status()

    data_responce = r.json()
    r.close()

    data_tree = make_files_dicts( data_responce )

    with open( os.path.join( os.getcwd(), CMAKEPM_DEPENDENCYLOCK_FILENAME ), 'w' ) as out_f:
        FORMAT = '{:20s} {:20s} {}\n'

        out_f.write(FORMAT.format( '# package', '# version', '# branch\n'))

        for (d_name, d_version, d_branch,) in deps_list:

            libs = data_tree[ d_name ][ d_branch ]
            
            def version_filter( v ):
                return all(map(lambda pair: pair[0] == '*' or int(pair[0]) == pair[1], zip(d_version, v[ 1 ])))

            versions = list(filter(version_filter, libs))

            current_version = max( versions, key=lambda x: x[ 1 ] )
            
            out_f.write( FORMAT.format(
                d_name,
                current_version[ 0 ],
                d_branch
            ))


if __name__ == '__main__':
    main()
