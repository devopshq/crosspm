#!/usr/bin/env python3
import argparse
import os
import pathlib

import shutil

def win32_fix_long_path(path):
    return os.path.realpath(path)

def move_to_origin( path_a, path_b_prefix ):
    str = "r\\?\\"
    path_b = os.path.join( path_a, path_b_prefix )
    path_a = win32_fix_long_path(path_a)
    if os.path.exists( path_b ):
        shutil.rmtree( path_b )

    def _ignore_path_b(path, names):
        if ( path == path_a )  and  ( path_b_prefix in names ):
            return [ path_b_prefix ]

        # nothing will be ignored
        return []

    shutil.copytree(
        path_a,
        path_b,
        symlinks=True,
        ignore=_ignore_path_b
    )

if __name__ == '__main__':
    move_to_origin('D:\\test','D:\\Documents')