#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

from crosspm.cpm import App

log = logging.getLogger(__name__)


def main():
    log.warning('Calling "pm_pack.py <args>" is DEPRECATED! Use "cmp.py pack <args>" instead!')

    sys.argv.insert(1, 'pack')
    app = App()
    app.run()


if __name__ == '__main__':
    main()
