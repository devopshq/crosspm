# -*- coding: utf-8 -*-
import logging
import os
# from crosspm.helpers.package import Package
from crosspm.helpers.exceptions import *
from datetime import datetime


class Cache(object):
    _clear = {}

    def __init__(self, config, cache_data):
        self._log = logging.getLogger('crosspm')
        self._config = config
        self._cache_path = config.crosspm_cache_root
        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        self.packed_path = os.path.realpath(os.path.join(self._cache_path, 'archive'))
        self.unpacked_path = os.path.realpath(os.path.join(self._cache_path, 'cache'))
        self.temp_path = os.path.realpath(os.path.join(self._cache_path, 'tmp'))

        self._clear = cache_data.get('clear', {})
        self._clear['size'] = self.str_to_size(self._clear.get('size', '0'))

    def str_to_size(self, size):
        _size = str(size).replace(' ', '').lower()
        try:
            _size0 = float(_size[:-2])
        except:
            _size0 = 0
        _measure = _size[-2:]
        if _measure == 'kb':
            _size = _size0 * 1024
        elif _measure == 'mb':
            _size = _size0 * 1024 * 1024
        elif _measure == 'gb':
            _size = _size0 * 1024 * 1024 * 1024
        else:
            try:
                _size = float(_size)
            except:
                _size = 0
        return _size

    def size_to_str(self, size, dec=0):
        try:
            _size = float(size)
        except:
            _size = 0
        _measure = 'b '
        _size0 = round(_size / 1024, 3)
        if _size0 >= 1.0:
            _measure = 'Kb'
            _size = _size0
            _size0 = round(_size / 1024, 3)
            if _size0 >= 1.0:
                _measure = 'Mb'
                _size = _size0
                _size0 = round(_size / 1024, 3)
                if _size0 >= 1.0:
                    _measure = 'Gb'
                    _size = _size0
        _size = round(_size, dec)
        if dec == 0:
            _size = int(_size)
        return '{:,} {}'.format(_size, _measure)

    def get_info(self, get_files=True):
        def get_dir(_dir_name, sub_dirs=True):
            res = {
                'path': _dir_name,
                'size': 0,
                'time': 0,
                'files': [],
                'folders': [],
            }
            for item in os.listdir(_dir_name):
                item_name = os.path.realpath(os.path.join(_dir_name, item))
                item_stat = os.stat(item_name)
                _size = getattr(item_stat, 'st_size', 0)
                _time = getattr(item_stat, 'st_ctime', datetime.now().timestamp())
                if os.path.isfile(os.path.join(_dir_name, item)):
                    res['size'] += _size
                    res['time'] = max(res['time'], _time)
                    res['files'].append({'size': _size,
                                         'time': _time,
                                         'path': item_name})
                elif sub_dirs:
                    _folder = get_dir(item_name)
                    res['folders'].append(_folder)
                    res['size'] += _folder['size']
                    res['time'] = max(res['time'], _folder['time'])
            return res

        total = {
            'packed': get_dir(self.packed_path),
            'unpacked': get_dir(self.unpacked_path),
            'temp': get_dir(self.temp_path),
            'other': get_dir(self._cache_path, False),
        }
        return total

    def _sort(self, item):
        return [item['time'], 0 - len(item['path'])]

    def info(self):
        print_stdout('Cache info:')

    def _delete_dir(self, _dir, time=None, size=None):
        _size = 0
        for _folder in _dir['folders']:
            _size += self._delete_dir(_folder)
            os.rmdir(_folder['path'])
        for _file in _dir['files']:
            _size += _file['size']
            os.remove(_file['path'])
        _dir['folders'].clear()
        _dir['files'].clear()
        _dir['size'] = 0
        return _size

    def clear(self, hard):

        # TODO: Check if given path is really crosspm cache before deleting anything!
        self._log.info('Clear cache{}'.format(' HARD! >:-E' if hard else ':'))

        max_size = self._clear.get('size', '0')
        total = self.get_info()

        self.size(total)

        # TEMP
        total_size = sum(
            (total['packed']['size'], total['unpacked']['size'], total['temp']['size'], total['other']['size']))
        cleared = self._delete_dir(total['temp'])

        # UNPACKED
        if hard:
            cleared += self._delete_dir(total['unpacked'])
        else:
            pass
            #
            # for folder in sorted(total['unpacked']['folders'], key=self._sort):
            #     if max_size:
            #         if total_size > max_size:
            #             total_size -= _rmdir(folder)

        # PACKED
        if hard:
            cleared += self._delete_dir(total['packed'])
        else:
            pass

        self._log.info('')
        self._log.info('Очищено: {}'.format(self.size_to_str(cleared, 1)))
        self._log.info('')
        self.size(total)

    def size(self, total=None):
        if not total:
            total = self.get_info(False)
        self._log.info('Cache size:')
        self._log.info('    packed: {:>15}'.format(self.size_to_str(total['packed']['size'], 1)))
        self._log.info('  unpacked: {:>15}'.format(self.size_to_str(total['unpacked']['size'], 1)))
        self._log.info('      temp: {:>15}'.format(self.size_to_str(total['temp']['size'], 1)))
        self._log.info('     other: {:>15}'.format(self.size_to_str(total['other']['size'], 1)))
        self._log.info('---------------------------')
        self._log.info('     total: {:>15}'.format(self.size_to_str(sum(
            (total['packed']['size'], total['unpacked']['size'], total['temp']['size'], total['other']['size'])), 1)))

    def age(self, total=None):
        if not total:
            total = self.get_info(False)
        oldest = min((x for x in (
            total['packed']['time'], total['unpacked']['time'], total['temp']['time'], total['other']['time']) if x))
        self._log.info('Cache oldest timestamp:')
        self._log.info('    packed: {}'.format(datetime.fromtimestamp(total['packed']['time'])))
        self._log.info('  unpacked: {}'.format(datetime.fromtimestamp(total['unpacked']['time'])))
        self._log.info('      temp: {}'.format(datetime.fromtimestamp(total['temp']['time'])))
        self._log.info('     other: {}'.format(datetime.fromtimestamp(total['other']['time'])))
        self._log.info('---------------------------')
        self._log.info('    oldest: {}'.format(datetime.fromtimestamp(oldest)))
