# -*- coding: utf-8 -*-
import logging


class BaseAdapter:
    def __init__(self, config):
        self._config = config
        self._log = logging.getLogger('crosspm')

    def get_packages(self, source, parser, downloader, list_or_file_path, property_validate=True):
        # Here must be function
        self._log.info('Get packages')
        return None

    def download_package(self, package, dest_path):
        # Here must be function
        self._log.info('Download package')
        return None, False
