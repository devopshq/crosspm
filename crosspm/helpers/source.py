# -*- coding: utf-8 -*-
# from crosspm.helpers.exceptions import *
import itertools
from string import Template

from addict import Dict


class Source:
    def __init__(self, adapter, parser, data):
        self._adapter = adapter
        self._parser = parser
        if 'repo' not in data:
            data['repo'] = ''
        if isinstance(data['repo'], str):
            data['repo'] = [data['repo']]
        self.args = {k: v for k, v in data.items() if k not in ['type', 'parser']}
        self.path_patterns = parser._rules['path']

    @property
    def repos(self):
        return self.args['repo']

    def get_packages(self, downloader, list_or_file_path, property_validate=True):
        return self._adapter.get_packages(self, self._parser, downloader, list_or_file_path, property_validate)

    def get_usedby(self, downloader, list_or_file_path, property_validate=True):
        return self._adapter.get_usedby(self, self._parser, downloader, list_or_file_path, property_validate)

    def __getattr__(self, item):
        return self.args.get(item, None)

    def __getitem__(self, item):
        return self.args.get(item, None)

    def get_paths(self, packages_to_find):
        paths = []

        for package, repo, path_pattern in itertools.product(packages_to_find, self.repos, self.path_patterns):
            params = {
                'server' : self.args['server'],
                'repo' : repo,
                'package' : package['package'],
                'version' : package['version']
            }
            paths.append(Dict({'path':path_pattern.format(**params), 'params':params}))

        return paths
