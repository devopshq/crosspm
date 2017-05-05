# -*- coding: utf-8 -*-
from crosspm.helpers.exceptions import *
import logging


class BaseAdapter:
    def __init__(self, config):
        self._config = config
        self._log = logging.getLogger('crosspm')

    def get_packages(self, source, parser, downloader, list_or_file_path):
        # Here must be function
        return None

    def download_package(self, package, dest_path):
        # Here must be function
        return None, False
