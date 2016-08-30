# -*- coding: utf-8 -*-
import os
import fnmatch
import logging

# third-party
import requests
from crosspm.helpers.config import CROSSPM_DEPENDENCY_LOCK_FILENAME
from crosspm.helpers.exceptions import *

log = logging.getLogger(__name__)


# TODO: REWORK PROMOTER COMPLETELY to match new architecture!!!
class Promoter:
    def __init__(self, config):
        self._config = config

    @staticmethod
    def get_version_int(version_str):
        parts = version_str.split('.')
        try:
            parts = list(map(int, parts))
            if len(parts) < 4:
                parts.insert(2, 0)
            return parts

        except ValueError:
            return [0] * 4

        except IndexError:
            return [0] * 4

    def parse_dir_list(self, data_dict, dir_list_data):
        for item in dir_list_data["files"]:
            if item["folder"]:
                continue

            parts = item["uri"].split('/')

            name = parts[1]
            branch = parts[2]
            version = parts[3]
            version_int = self.get_version_int(version)

            data_dict.setdefault(name, {})
            data_dict[name].setdefault(branch, [])
            data_dict[name][branch].append((version, version_int))

    @staticmethod
    def join_package_path(server_url, part_a, repo, path):
        server_url = server_url if not server_url.endswith('/') else server_url[: -1]
        part_a = part_a if not part_a.startswith('/') else part_a[1:]
        part_a = part_a if not part_a.endswith('/') else part_a[: -1]
        repo = repo if not repo.startswith('/') else repo[1:]
        repo = repo if not repo.endswith('/') else repo[: -1]
        path = path if not path.startswith('/') else path[1:]

        return '{server_url}/{part_a}/{repo}/{path}'.format(**locals())

    def promote_packages(self):
        data_tree = {}
        deps_list = []  # pm_common.get_dependencies(os.path.join(os.getcwd(), CROSSPM_DEPENDENCY_FILENAME))
        out_file_data_str = ''
        out_file_format = '{:20s} {:20s} {}\n'
        out_file_path = os.path.join(os.getcwd(), CROSSPM_DEPENDENCY_LOCK_FILENAME)

        # clean file
        with open(out_file_path, 'w') as out_f:
            out_f.write(out_file_format.format('# package', '# version', '# branch\n'))

        for current_source in self._config['sources']:
            for current_repo in current_source['repo']:
                request_url = self.join_package_path(
                    current_source['server'],
                    'api/storage',
                    current_repo,
                    '?list&deep=1&listFolders=0&mdTimestamps=1&includeRootPath=1',
                )

                log.info('GET request: %s', request_url)

                r = requests.get(
                    request_url,
                    verify=False,
                    auth=current_source['auth'],
                )

                r.raise_for_status()

                data_response = r.json()

                self.parse_dir_list(data_tree, data_response)

        for (d_name, d_version, d_branch,) in deps_list:
            if d_name not in data_tree:
                raise CrosspmException(
                    CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
                    'unknown package [{}]'.format(d_name),
                )

            if d_branch not in data_tree[d_name]:
                raise CrosspmException(
                    CROSSPM_ERRORCODE_PACKAGE_BRANCH_NOT_FOUND,
                    'unknown branch [{}] of package [{}]'.format(
                        d_branch,
                        d_name,
                    ))

            libs = data_tree[d_name][d_branch]

            versions = [v for v in libs if fnmatch.fnmatch(v[0], '.'.join(d_version))]

            if not versions:
                raise CrosspmException(
                    CROSSPM_ERRORCODE_VERSION_PATTERN_NOT_MATCH,
                    'pattern [{ver}] does not match any version of package [{pkg}] for branch [{br}] '.format(
                        ver='.'.join(d_version),
                        pkg=d_name,
                        br=d_branch,
                    ))

            current_version = max(versions, key=lambda x: x[1])

            out_file_data_str += out_file_format.format(
                d_name,
                current_version[0],
                d_branch
            )

        with open(out_file_path, 'w') as out_f:
            out_f.write(out_file_data_str)
