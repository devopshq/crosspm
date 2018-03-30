# -*- coding: utf-8 -*-
# from crosspm.helpers.exceptions import *


class Source:
    def __init__(self, adapter, parser, data):
        self._adapter = adapter
        self._parser = parser
        if 'repo' not in data:
            data['repo'] = ''
        if isinstance(data['repo'], str):
            data['repo'] = [data['repo']]
        self.args = {k: v for k, v in data.items() if k not in ['type', 'parser']}

    def get_packages(self, downloader, list_or_file_path):
        return self._adapter.get_packages(self, self._parser, downloader, list_or_file_path)

    def __getattr__(self, item):
        return self.args.get(item, None)

    def __getitem__(self, item):
        return self.args.get(item, None)
