# -*- coding: utf-8 -*-
import os
import contextlib
import tarfile
import shutil
import zipfile

from crosspm.helpers.exceptions import *


class Archive(object):
    @staticmethod
    def create(archive_name, src_dir_path):
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

    @staticmethod
    def extract(archive_name, dst_dir_path, file_name=None):
        dst_dir_path_tmp = '{}_tmp'.format(dst_dir_path)

        # remove temp dir
        if os.path.exists(dst_dir_path_tmp):
            shutil.rmtree(dst_dir_path_tmp)

        if tarfile.is_tarfile(archive_name):
            with contextlib.closing(tarfile.TarFile.open(archive_name, 'r:*')) as tf:
                if file_name:
                    tf.extract(file_name, path=dst_dir_path_tmp)
                else:
                    tf.extractall(path=dst_dir_path_tmp)

        elif zipfile.is_zipfile(archive_name):
            with contextlib.closing(zipfile.ZipFile(archive_name, mode='r')) as zf:
                if file_name:
                    zf.extract(file_name, path=dst_dir_path_tmp)
                else:
                    zf.extractall(path=dst_dir_path_tmp)

        else:
            raise CrosspmException(
                CROSSPM_ERRORCODE_UNKNOWN_ARCHIVE,
                'unknown archive type. File: [{}]'.format(archive_name),
            )

        # remove temp dir
        if os.path.exists(dst_dir_path):
            shutil.rmtree(dst_dir_path)
        os.renames(dst_dir_path_tmp, dst_dir_path)

    @staticmethod
    def extract_file(archive_name, dst_dir_path, file_name):
        try:
            Archive.extract(archive_name, dst_dir_path, file_name)
            _dest_file = os.path.join(dst_dir_path, file_name)
        except:
            _dest_file = None
        return _dest_file
