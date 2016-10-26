# -*- coding: utf-8 -*-
import os
# from crosspm.helpers.package import Package
from crosspm.helpers.exceptions import *


class Cache(object):
    def __init__(self, config):
        self._config = config
        self._cache_path = config.crosspm_cache_root
        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        self.packed_path = os.path.realpath(os.path.join(self._cache_path, 'archive'))
        self.unpacked_path = os.path.realpath(os.path.join(self._cache_path, 'cache'))
        self.temp_path = os.path.realpath(os.path.join(self._cache_path, 'tmp'))

    def info(self):
        print_stdout('Cache info:')

    def clear(self):
        # TODO: Check if given path is really crosspm cache before deleting anything!
        print_stdout('Clear cache:')
