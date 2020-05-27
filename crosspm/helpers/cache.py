# -*- coding: utf-8 -*-
import logging
import os
import time
# from crosspm.helpers.package import Package
from datetime import datetime, timedelta


class Cache:
    def __init__(self, config, cache_data):
        self._log = logging.getLogger('crosspm')
        self._config = config
        self._cache_path = config.crosspm_cache_root
        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        self.path = {
            'packed': os.path.realpath(os.path.join(self._cache_path, 'archive')),
            'unpacked': os.path.realpath(os.path.join(self._cache_path, 'cache')),
        }
        self.temp_path = os.path.realpath(os.path.join(self._cache_path, 'tmp'))

        self._clear = cache_data.get('clear', {})
        self._clear['auto'] = self._clear.get('auto', False)
        if isinstance(self._clear['auto'], str):
            if self._clear['auto'].lower() in ['0', 'no', '-', 'false']:
                self._clear['auto'] = False
        try:
            self._clear['auto'] = bool(self._clear['auto'])
        except Exception:
            self._clear['auto'] = False

        self._clear['size'] = self.str_to_size(self._clear.get('size', '0'))

        try:
            self._clear['days'] = int(self._clear.get('days', '0'))
        except Exception:
            self._clear['days'] = 0

        _unique = config.get_fails('unique', None)
        self._storage = cache_data.get('storage', {'packed': '', 'unpacked': ''})
        if not self._storage['packed']:
            if _unique and isinstance(_unique, (list, tuple)):
                self._storage['packed'] = '/'.join('{%s}' % x for x in _unique)
                if self._storage['packed']:
                    self._storage['packed'] += '/{filename}'

        if not self._storage['packed']:
            self._storage['packed'] = '{%s}/{filename}' % config.name_column

        if not self._storage['unpacked']:
            if _unique and isinstance(_unique, (list, tuple)):
                self._storage['unpacked'] = '/'.join('{%s}' % x for x in _unique)

        if not self._storage['unpacked']:
            self._storage['unpacked'] = '{%s}' % config.name_column

    def str_to_size(self, size):
        _size = str(size).replace(' ', '').lower()
        try:
            _size0 = float(_size[:-2])
        except Exception:
            _size0 = 0
        _measure = _size[-2:]
        if _measure == 'kb':
            _size = _size0 * 1024
        elif _measure == 'mb':
            _size = _size0 * 1024 * 1024
        elif _measure == 'gb':
            _size = _size0 * 1024 * 1024 * 1024
        else:
            if _size[-1] == 'b':
                _size = _size[:-1]
            try:
                _size = float(_size)
            except Exception:
                _size = 0
        return _size

    def size_to_str(self, size, dec=0):
        try:
            _size = float(size)
        except Exception:
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
            if os.path.isdir(_dir_name):
                for item in os.listdir(_dir_name):
                    item_name = os.path.realpath(os.path.join(_dir_name, item))
                    item_stat = os.stat(item_name)
                    _size = getattr(item_stat, 'st_size', 0)
                    _now = datetime.now()
                    _time = getattr(item_stat, 'st_ctime',
                                    time.mktime(_now.timetuple()) + float(_now.microsecond) / 1000000.0)
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
            'packed': get_dir(self.path['packed']),
            'unpacked': get_dir(self.path['unpacked']),
            'temp': get_dir(self.temp_path),
            'other': get_dir(self._cache_path, False),
        }
        return total

    def _sort(self, item):
        return item['time']

    def info(self):
        print("Cache info:")

    def _delete_dir(self, _dirs, max_time=None, del_size=None):
        cleared = [0]

        def do_delete_dir(_dir):
            _size = 0
            folders_to_delete = []
            files_to_delete = []
            for _folder in _dir['folders']:
                _size += do_delete_dir(_folder)
                if len(_folder['folders']) + len(_folder['files']) == 0:
                    os.rmdir(_folder['path'])
                    folders_to_delete += [_folder]
            for _file in _dir['files']:
                do_clear = False
                if max_time:
                    if max_time > _file['time']:
                        do_clear = True
                if del_size:
                    if del_size > cleared[0]:
                        do_clear = True
                if not (max_time or del_size):
                    do_clear = True
                if do_clear:
                    _size += _file['size']
                    cleared[0] += _file['size']
                    os.remove(_file['path'])
                    files_to_delete += [_file]
            _dir['size'] -= _size
            for _folder in folders_to_delete:
                _dir['folders'].remove(_folder)
            for _file in files_to_delete:
                _dir['files'].remove(_file)
            return _size

        return do_delete_dir(_dirs)

    def auto_clear(self):
        if self._clear['auto']:
            self.clear(False, True)

    def clear(self, hard=False, auto=False):

        # TODO: Check if given path is really crosspm cache before deleting anything!
        _now = datetime.now().timestamp()
        self._log.info('Read cache...')
        max_size = self._clear['size']
        if self._clear['days']:
            max_time = _now - timedelta(days=self._clear['days']).total_seconds()
        else:
            max_time = 0

        total = self.get_info()

        total_size = sum(total[x]['size'] for x in total)
        oldest = min(total[x]['time'] if total[x]['time'] else _now for x in total)

        if auto and not hard:
            do_clear = False
            if max_size and max_size < total_size:
                do_clear = True
            if max_time and max_time > oldest:
                do_clear = True
            if not do_clear:
                return

        self._log.info('Clear cache{}'.format(' HARD! >:-E' if hard else ':'))

        self.size(total)

        # TEMP
        cleared = self._delete_dir(total['temp'])

        # UNPACKED
        if hard:
            cleared += self._delete_dir(total['unpacked'])
        else:
            folders_to_delete = []
            _size = 0
            for folder in sorted(total['unpacked']['folders'], key=self._sort):
                do_clear = False
                if max_size:
                    if total_size - cleared - _size > max_size:
                        do_clear = True
                if max_time:
                    if folder['time'] < max_time:
                        do_clear = True
                if do_clear:
                    _size += self._delete_dir(folder)
                if len(folder['folders']) + len(folder['files']) == 0:
                    os.rmdir(folder['path'])
                    folders_to_delete += [folder]
                    # if (not do_clear) and (not max_time):
                    #     break
            total['unpacked']['size'] -= _size
            cleared += _size
            for folder in folders_to_delete:
                total['unpacked']['folders'].remove(folder)

        # PACKED
        if hard:
            cleared += self._delete_dir(total['packed'])
        else:
            del_size = total_size - cleared - max_size
            if del_size < 0:
                del_size = 0
            if del_size or max_time:
                cleared += self._delete_dir(total['packed'], max_time, del_size)

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
        self._log.info('     total: {:>15}'.format(self.size_to_str(sum(total[x]['size'] for x in total), 1)))

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

    def path_packed(self, package=None, params=None):
        return self.path_any('packed', package, params)

    def path_unpacked(self, package=None, params=None):
        return self.path_any('unpacked', package, params)

    def path_any(self, name, package=None, params=None):
        if params:
            tmp_params = {}
            for k, v in params.items():
                if isinstance(v, list):
                    v = ".".join([x for x in v if x is not None and x != ''])
                tmp_params[k] = v
            res = self._storage[name].format(**tmp_params)
        elif package:
            res = self._storage[name].format(**(package.get_params(merged=True)))
        else:
            res = ''
        res = os.path.realpath(os.path.join(self.path[name], res))
        return res

    def exists_packed(self, package=None, params=None, pkg_path='', check_stat=True):
        # Check if file exists and size and time match
        path = self.path_packed(package, params) if not pkg_path else pkg_path
        res = os.path.exists(path)
        if res and package and check_stat:
            _stat_attr = {'ctime': 'st_atime',
                          'mtime': 'st_mtime',
                          'size': 'st_size'}
            _stat_file = os.stat(path)
            if any(package.stat[k] != getattr(_stat_file, v, -999) for k, v in _stat_attr.items()):
                res = False
                os.remove(path)

        return res, path

    def exists_unpacked(self, package, filename=None, params=None, pkg_path=''):
        # TODO: Check if file exists and size and time match
        path = self.path_unpacked(package, params) if not pkg_path else pkg_path
        if os.path.isdir(path):
            # check that dir is not empty
            res = bool(os.listdir(path))
        else:
            res = os.path.exists(path)

        return res, path
