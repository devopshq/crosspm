# -*- coding: utf-8 -*-

# TODO: it's better to use six module
from __future__ import print_function  # support for print to stderr from Python 2.7

import contextlib
import json
import logging
import os
import shutil
import sys
import tarfile
import zipfile

from requests.packages.urllib3 import disable_warnings

disable_warnings()

log = logging.getLogger(__name__)

CROSSPM_DEPENDENCY_FILENAME = 'dependencies.txt'
CROSSPM_DEPENDENCY_LOCK_FILENAME = '{}.lock'.format(CROSSPM_DEPENDENCY_FILENAME)
CROSSPM_CONFIG_DEFAULT_FILENAME = 'crosspm.config'

CROSSPM_ERRORCODES = (
    CROSSPM_ERRORCODE_SUCCESS,
    CROSSPM_ERRORCODE_UNKNOWN_ERROR,
    CROSSPM_ERRORCODE_WRONG_ARGS,
    CROSSPM_ERRORCODE_FILE_DEPS_NOT_FOUND,
    CROSSPM_ERRORCODE_WRONG_SYNTAX,
    CROSSPM_ERRORCODE_MULTIPLE_DEPS,
    CROSSPM_ERRORCODE_NO_FILES_TO_PACK,
    CROSSPM_ERRORCODE_SERVER_CONNECT_ERROR,
    CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
    CROSSPM_ERRORCODE_PACKAGE_BRANCH_NOT_FOUND,
    CROSSPM_ERRORCODE_VERSION_PATTERN_NOT_MATCH,
    CROSSPM_ERRORCODE_UNKNOWN_OUT_TYPE,
    CROSSPM_ERRORCODE_FILE_IO,
    CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
    CROSSPM_ERRORCODE_CONFIG_IO_ERROR,
    CROSSPM_ERRORCODE_UNKNOWN_ARCHIVE,
) = range(16)

OPT_SOURCES = []


class CrosspmException(Exception):
    def __init__(self, error_code, msg=''):
        super().__init__(msg)
        self.error_code = error_code
        self.msg = msg


class CrosspmExceptionWrongArgs(CrosspmException):
    def __init__(self, msg=''):
        super().__init__(CROSSPM_ERRORCODE_WRONG_ARGS, msg)


def print_stderr(*args, **kwargs):
    kwargs.update({'file': sys.stderr})
    print(*args, **kwargs)


def get_crosspm_cache_root():
    root = os.getenv('CROSSPM_CACHE_ROOT')

    if not root:
        home_dir = os.getenv('APPDATA') if os.name == 'nt' else os.getenv('HOME')
        root = os.path.join(home_dir, '.crosspm')

    return root


def get_package_params(i, line):
    parts = line.split()
    n = len(parts)

    if n not in (2, 3,):
        raise CrosspmException(
            CROSSPM_ERRORCODE_WRONG_SYNTAX,
            'wrong syntax at line {}. File: [{}]'.format(i, parts[0])
        )

    name = parts[0]
    version = tuple(parts[1].split('.'))
    branch = parts[2] if n == 3 else 'master'

    return name, version, branch


def get_dependencies(file_path):
    result = []

    if not os.path.exists(file_path):
        raise CrosspmException(
            CROSSPM_ERRORCODE_FILE_DEPS_NOT_FOUND,
            'file not found: [{}]'.format(file_path),
        )

    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            result.append(get_package_params(i, line))

        return result


def create_archive(archive_name, src_dir_path):
    archive_name = os.path.realpath(archive_name)
    src_dir_path = os.path.realpath(src_dir_path)
    files_to_pack = []
    archive_name_tmp = os.path.join(
        os.path.dirname(archive_name),
        'tmp_{}'.format(os.path.basename(archive_name)),
    )

    for name in os.listdir(src_dir_path):
        current_path = os.path.join(src_dir_path, name)
        real_path = os.path.realpath(current_path)
        rel_path = os.path.relpath(current_path, src_dir_path)

        files_to_pack.append((real_path, rel_path,))

    if not files_to_pack:
        raise CrosspmException(
            CROSSPM_ERRORCODE_NO_FILES_TO_PACK,
            'no files to pack, directory [{}] is empty'.format(
                src_dir_path
            ),
        )

    with contextlib.closing(tarfile.TarFile.open(archive_name_tmp, 'w:gz')) as tf:
        for real_path, rel_path in files_to_pack:
            tf.add(real_path, arcname=rel_path)

    os.renames(archive_name_tmp, archive_name)


def extract_archive(archive_name, dst_dir_path):
    dst_dir_path_tmp = '{}_tmp'.format(dst_dir_path)

    # remove temp dir
    if os.path.exists(dst_dir_path_tmp):
        shutil.rmtree(dst_dir_path_tmp)

    if tarfile.is_tarfile(archive_name):
        with contextlib.closing(tarfile.TarFile.open(archive_name, 'r:*')) as tf:
            tf.extractall(path=dst_dir_path_tmp)

    elif zipfile.is_zipfile(archive_name):
        with contextlib.closing(zipfile.ZipFile(archive_name, mode='r')) as zf:
            zf.extractall(path=dst_dir_path_tmp)

    else:
        raise CrosspmException(
            CROSSPM_ERRORCODE_UNKNOWN_ARCHIVE,
            'unknown archive type. File: [{}]'.format(archive_name),
        )

    os.renames(dst_dir_path_tmp, dst_dir_path)


def read_config(file_path=None):
    """
    order of priority:
     - option "--config" passed to script or argument file_path of api call
     - environment variable "CROSSPM_CONFIG_PATH"
     - file "crosspm.config" located at working dir
    """

    if file_path is None:
        env_var_name = 'CROSSPM_CONFIG_PATH'
        config_path_env = os.getenv(env_var_name)
        config_path_cwd = os.path.join(os.getcwd(), CROSSPM_CONFIG_DEFAULT_FILENAME)

        if config_path_env:
            log.info('Environment variable CROSSPM_CONFIG_PATH is set')
            file_path = config_path_env

        elif os.path.exists(config_path_cwd):
            log.info('Found config file at working directory [%s]', config_path_cwd)
            file_path = config_path_cwd

        else:
            raise CrosspmException(
                CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
                'path to config file is not set',
            )

    file_path = os.path.realpath(file_path)

    if not os.path.exists(file_path):
        raise CrosspmException(
            CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
            'config file not found at given path: [{}]'.format(file_path)
        )

    log.info('Reading config file... [%s]', file_path)

    try:
        with open(file_path) as f:
            result = json.loads(f.read())

    except Exception as e:
        log.exception(e)

        code = CROSSPM_ERRORCODE_CONFIG_IO_ERROR
        msg = 'catch exception while reading config file: [{}]'.format(
            file_path,
        )

        raise CrosspmException(code, msg) from e

    return result


def parse_config(data):
    result = {
        'sources': [],
    }

    for item_str in data['sources']:
        item_list = item_str.split()

        result['sources'].append({
            'connector_type': item_list[0],
            'server_url': item_list[1],
            'repos': [x.strip() for x in item_list[2].split(',')],
            'auth_type': item_list[3],
            'auth': (item_list[4], item_list[5],),
        })

    return result


def load_config(file_path=None):
    config_data = read_config(file_path)
    config_dict = parse_config(config_data)

    OPT_SOURCES.extend(config_dict['sources'])
