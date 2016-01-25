#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import cpm


def main():

    sys.stderr.write('\n\nWARNING! Calling "pm_pack.py <args>" is DEPRECATED!\n\tUse "cmp.py pack <args>" instead!\n\n')
    sys.stderr.flush()
    
    sys.argv.insert( 1, 'pack' )

    cpm.main()
    

if __name__ == '__main__':
    main()