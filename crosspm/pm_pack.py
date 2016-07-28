#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

import __main__ as crosspm

log = logging.getLogger(__name__)


def main():
    log.warning('Calling "pm_pack.py <args>" is DEPRECATED! Use "cmp.py pack <args>" instead!')

    sys.argv.insert(1, 'pack')
    crosspm.main()


if __name__ == '__main__':
    main()
