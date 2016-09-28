#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

from crosspm.cpm import App

log = logging.getLogger(__name__)


def main():
    log.warning('Calling "pm_promote_deps.py <args>" is DEPRECATED! Use "cmp.py promote <args>" instead!')

    sys.argv.insert(1, 'promote')
    app = App()
    app.run()


if __name__ == '__main__':
    main()
