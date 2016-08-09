# -*- coding: utf-8 -*-
import json
import flask
import pytest

from crosspm.helpers.connectors import (
    _connectors_dict,
    get_connector,
    repo_scheme_crosspm_simple,
    repo_scheme_nuget_simple,
    ConnectorBase,
    ConnectorJfrogArtifactory,
)


def test_connectors_dict():
    assert _connectors_dict == {
        'jfrog-artifactory': ConnectorJfrogArtifactory,
    }


def test_get_connector():
    assert get_connector('jfrog-artifactory') is ConnectorJfrogArtifactory

    with pytest.raises(KeyError) as e:
        get_connector('some_name')


def test_connectorjfrogartifactory():
    assert issubclass(ConnectorJfrogArtifactory, ConnectorBase)


@pytest.mark.usefixtures('live_server')
class TestArtifactory():
    def getConnector(self):
        server_url = flask.url_for('index', _external=True)

        c = get_connector('jfrog-artifactory')({
            'server_url': server_url,
            'repos': 'libs',
            'auth_type': 'basic',
            'auth': ('auth', 'password',),
        })

        return c

    def test_list(self):
        c = self.getConnector()

        assert c.list()


def test_parse_list_nuget():
    c = get_connector('jfrog-artifactory')({
        'server_url': 'localhost',
        'repos': 'libs',
        'auth_type': 'basic',
        'auth': ('auth', 'password',),
    })

    c.apply_scheme(repo_scheme_nuget_simple)

    with open('repo_nuget.json') as f:
        data = json.load(f)

    items = c.parse_list(data)

    assert items


def test_parse_list_extlibs():
    c = get_connector('jfrog-artifactory')({
        'server_url': 'localhost',
        'repos': 'libs',
        'auth_type': 'basic',
        'auth': ('auth', 'password',),
    })

    c.apply_scheme(repo_scheme_crosspm_simple)

    with open('repo_extlibs.json') as f:
        data = json.load(f)

    items = c.parse_list(data)

    assert items
