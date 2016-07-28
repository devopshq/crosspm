#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

import __main__ as crosspm

log = logging.getLogger(__name__)


def main():
    log.warning('Calling "pm_promote_deps.py <args>" is DEPRECATED! Use "cmp.py promote <args>" instead!')

    sys.argv.insert(1, 'promote')
    crosspm.main()


if __name__ == '__main__':
    main()
