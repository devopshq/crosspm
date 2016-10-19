# -*- coding: utf-8 -*-
import requests
import os
from crosspm.helpers.package import Package
from crosspm.helpers.exceptions import *


class BaseAdapter(object):
    def __init__(self, config):
        self._config = config

    def get_packages(self, source, parser, downloader, list_or_file_path):
        # Here must be function
        return None

    def download_package(self, package, dest_path):
        # Here must be function
        return None, False
