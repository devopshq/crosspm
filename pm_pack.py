#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from helpers import pm_common

def main():
    
    pm_common.createArchive(
        sys.argv[ 1 ],  # archive_name
        sys.argv[ 2 ],  # src_dir_path
    )
    
if __name__ == '__main__':
    main()