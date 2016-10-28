# -*- coding: utf-8 -*-
import os
# from crosspm.helpers.package import Package
from crosspm.helpers.exceptions import *
from datetime import datetime


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

    def clear(self, hard):
        # TODO: Check if given path is really crosspm cache before deleting anything!
        print_stdout('Clear cache{}'.format(' HARD! >:-E' if hard else ':'))

    def size(self):
        # TODO: Check if given path is really crosspm cache before deleting anything!
        size_packed = 0
        size_unpacked = 0
        size_temp = 0
        size_other = 0
        for (cur_dir, sub_dirs, files) in os.walk(self._cache_path):
            for file in files:
                filename = os.path.realpath(os.path.join(cur_dir, file))
                stat_file = os.stat(filename)
                size = getattr(stat_file, 'st_size', 0)
                # os.path.commonpath((cur_dir,self.packed_path)) == self.packed_path
                if cur_dir.startswith(self.packed_path):
                    size_packed += size
                elif cur_dir.startswith(self.unpacked_path):
                    size_unpacked += size
                elif cur_dir.startswith(self.temp_path):
                    size_temp += size
                else:
                    size_other += size

        print_stdout('Cache size:\n'
                     '    packed: {packed:>15,}\n'
                     '  unpacked: {unpacked:>15,}\n'
                     '      temp: {temp:>15,}\n'
                     '     other: {other:>15,}\n'
                     '---------------------------\n'
                     '     total: {total:>15,}\n'.format(
            packed=size_packed,
            unpacked=size_unpacked,
            temp=size_temp,
            other=size_other,
            total=sum((size_packed, size_unpacked, size_temp, size_other))
        ))

    def age(self):
        time_packed = 0.0
        time_unpacked = 0.0
        time_temp = 0.0
        time_other = 0.0
        for (cur_dir, sub_dirs, files) in os.walk(self._cache_path):
            for file in files:
                filename = os.path.realpath(os.path.join(cur_dir, file))
                stat_file = os.stat(filename)
                time = getattr(stat_file, 'st_ctime', None)
                # os.path.commonpath((cur_dir,self.packed_path)) == self.packed_path
                if time:
                    if cur_dir.startswith(self.packed_path):
                        time_packed = min(time, time_packed) or time
                    elif cur_dir.startswith(self.unpacked_path):
                        time_unpacked = min(time, time_unpacked) or time
                    elif cur_dir.startswith(self.temp_path):
                        time_temp = min(time, time_temp) or time
                    else:
                        time_other = min(time, time_other) or time
        oldest = min((x for x in (time_packed, time_unpacked, time_temp, time_other) if x))
        print_stdout('Cache oldest timestamp:\n'
                     '    packed: {packed}\n'
                     '  unpacked: {unpacked}\n'
                     '      temp: {temp}\n'
                     '     other: {other}\n'
                     '---------------------------\n'
                     '    oldest: {oldest}\n'.format(
            packed=datetime.fromtimestamp(time_packed),
            unpacked=datetime.fromtimestamp(time_unpacked),
            temp=datetime.fromtimestamp(time_temp),
            other=datetime.fromtimestamp(time_other),
            oldest=datetime.fromtimestamp(oldest)
        ))
