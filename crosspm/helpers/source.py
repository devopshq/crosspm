# -*- coding: utf-8 -*-
# from crosspm.helpers.exceptions import *


class Source(object):
    _adapter = None
    _parser = None
    args = {}

    def __init__(self, adapter, parser, data):
        self._adapter = adapter
        self._parser = parser
        if 'repo' not in data:
            data['repo'] = ''
        if type(data['repo']) is str:
            data['repo'] = [data['repo']]
        self.args = {k: v for k, v in data.items() if k not in ['type', 'parser']}

    def get_packages(self, downloader, list_or_file_path):
        return self._adapter.get_packages(self, self._parser, downloader, list_or_file_path)
