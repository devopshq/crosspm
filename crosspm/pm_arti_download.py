#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

from crosspm.cpm import App

log = logging.getLogger(__name__)


def main():
    log.warning('Calling "pm_arti_download.py <args>" is DEPRECATED! Use "cmp.py download <args>" instead!')

    sys.argv.insert(1, 'download')
    app = App()
    app.run()


if __name__ == '__main__':
    main()
