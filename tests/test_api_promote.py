# -*- coding: utf-8 -*-
import io
import json

import flask
import pytest

import helpers.promoter as api
from crosspm.helpers import dependency_parser

config_a = """
{
    "schemes": {
        "nuget": {
            "pkg_params": {
                "name":    [ "artifact.property", "nuget.id", 0, false, false ],
                "version": [ "artifact.property", "nuget.version", 0, false, false ],
                "release": [ "artifact.property", "devops.release.*", null, true, true ],
                "quality": [ "artifact.property_map", "devops.release.*", 0 ]
            }
        }
    },
    "sources": [
        "jfrog-artifactory %SERVER_URL% libs nuget basic user password"
    ]
}
"""

deps_txt = """
# some comments
--contract=quality:1
AAA * devops.release.r12 stable
#BBB * devops.release.r12 integration
"""

# TODO: REWORK TEST COMPLETELY !!!

@pytest.mark.usefixtures('live_server')
class TestApiPromote():
    def test_a(self):

        server_url = flask.url_for('index', _external=True)
        config = config_a.replace('%SERVER_URL%', server_url)
        promoter = api.CrosspmPromoter()
        downloader = api.CrosspmDownloader()
        deps_lock_fd = io.StringIO()

        promoter.set_config(json.loads(config))
        downloader.set_config(json.loads(config))

        parser = dependency_parser.DependencyParser('simple')
        deps = parser.parse(deps_txt.split('\n'))

        promoter.set_dependencies(deps)

        promoted_deps = promoter.promote_packages()

        for x in promoted_deps:
            print(x[0].package_name(), x[1])

        promoter.save_deps_to_file_obj(deps_lock_fd, promoted_deps)

        for line in deps_lock_fd.getvalue().split('\n'):
            print(line)
            # print( deps_lock_fd.getvalue() )

        downloader.get_packages(promoted_deps, ('nix', 'x86_64', 'gcc-5.2'), (None, None, None))

        assert None
