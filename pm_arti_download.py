#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

import cpm


def main():

    sys.stderr.write('\n\nWARNING! Calling "pm_promote_deps.py <args>" is DEPRECATED!\n\tUse "cmp.py promote <args>" instead!\n\n')
    sys.stderr.flush()

    sys.argv.insert( 1, 'download' )

    cpm.main()


if __name__ == '__main__':
    main()
