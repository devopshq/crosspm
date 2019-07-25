# -*- coding: utf-8 -*-
import contextlib
import os
import shutil
import sys
import tarfile
import zipfile

from crosspm.helpers.exceptions import CrosspmException, CROSSPM_ERRORCODE_NO_FILES_TO_PACK, \
    CROSSPM_ERRORCODE_UNKNOWN_ARCHIVE

WINDOWS = True if sys.platform == 'win32' else False


class Archive:
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
        # HACK for https://bugs.python.org/issue18199
        if WINDOWS:
            dst_dir_path = "\\\\?\\" + dst_dir_path

        dst_dir_path_tmp = '{}_tmp'.format(dst_dir_path)

        # remove temp dir
        if os.path.exists(dst_dir_path_tmp):
            shutil.rmtree(dst_dir_path_tmp)
        if os.path.exists(dst_dir_path):
            os.renames(dst_dir_path, dst_dir_path_tmp)

        # TODO: remove hack for deb-package
        # ------- START deb-package -------
        if archive_name.endswith(".deb"):
            # На Windows:
            # deb-пакет содержит в себе data.tar файл
            # Распаковываем deb в первый раз, сохраняя data.tar рядом с deb-файлом
            # Затем, подменяет имя архива и пускаем по обычному пути распаковки,
            # чтобы он нашел tar и распаковал его как обычно
            if WINDOWS:
                datatar_dir = os.path.dirname(archive_name)
                if not os.path.exists(datatar_dir):
                    os.makedirs(datatar_dir)
                from pyunpack import Archive
                Archive(archive_name).extractall(datatar_dir)
                # Подмена имени
                archive_name = os.path.join(datatar_dir, 'data.tar')
            # На linux - распаковываем сразу
            else:
                from pyunpack import Archive
                if not os.path.exists(dst_dir_path):
                    os.makedirs(dst_dir_path)
                Archive(archive_name).extractall(dst_dir_path)
        # ------- END deb-package -------

        if tarfile.is_tarfile(archive_name):
            with contextlib.closing(tarfile.TarFile.open(archive_name, 'r:*')) as tf:
                if file_name:
                    tf.extract(file_name, path=dst_dir_path)
                else:
                    # Quick hack for unpack tgz on Windows with PATH like \\?\C:
                    # Internal issue: CM-39214
                    try:
                        tf.extractall(path=dst_dir_path)
                    except OSError:
                        dst_dir_path = dst_dir_path.replace("\\\\?\\", '')
                        tf.extractall(path=dst_dir_path)

        elif zipfile.is_zipfile(archive_name):
            with contextlib.closing(zipfile.ZipFile(archive_name, mode='r')) as zf:
                if file_name:
                    zf.extract(file_name, path=dst_dir_path)
                else:
                    zf.extractall(path=dst_dir_path)

        elif archive_name.endswith('.rar'):
            if not os.path.exists(dst_dir_path):
                os.makedirs(dst_dir_path)
            from pyunpack import Archive
            Archive(archive_name).extractall(dst_dir_path)

        elif archive_name.endswith('.deb'):
            # We unpack above
            pass

        else:
            tries = 0
            while tries < 3:
                tries += 1
                try:
                    if os.path.exists(dst_dir_path):
                        shutil.rmtree(dst_dir_path)
                    if os.path.exists(dst_dir_path_tmp):
                        os.renames(dst_dir_path_tmp, dst_dir_path)
                    tries = 3
                except Exception:
                    pass
            raise CrosspmException(
                CROSSPM_ERRORCODE_UNKNOWN_ARCHIVE,
                'unknown archive type. File: [{}]'.format(archive_name),
            )

        # remove temp dir
        if os.path.exists(dst_dir_path_tmp):
            shutil.rmtree(dst_dir_path_tmp)

    @staticmethod
    def extract_file(archive_name, dst_dir_path, file_name):

        try:
            Archive.extract(archive_name, dst_dir_path, file_name)
            _dest_file = os.path.join(dst_dir_path, file_name)
        except Exception:
            _dest_file = None
        return _dest_file
