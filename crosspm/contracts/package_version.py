import re

from packaging.version import parse as parse_version, Version

CROSSPM_VERSION_PATTERN = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\-(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
"""

class PackageVersion(Version):

    _regex = re.compile(r"^\s*" + CROSSPM_VERSION_PATTERN + r"\s*$", re.VERBOSE | re.IGNORECASE)

    def __init__(self, version):
        super(PackageVersion, self).__init__(version)
        self._version_original_str = version

    # cant use base Version.__str__, because 'local' placeholder normalized, and all '[-_]' are changed with '.'
    def __str__(self):
        return self._version_original_str
