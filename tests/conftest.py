# -*- coding: utf-8 -*-
import json
import os

import pytest
import flask


@pytest.fixture
def app():
    app = flask.Flask(__name__)

    @app.route('/')
    def index():
        return "JFrog Artifactory"

    @app.route('/api/search/artifact', methods=['GET'])  # TODO: '/<name>/<repos>'
    def apilist():
        # request.args.get('key', '')

        # resp = make_response(, 200)
        # resp.headers['X-Something'] = 'A value'

        filename = os.path.realpath('test_repo_nuget2.json')

        with open(filename) as f:
            data = json.load(f)

        return flask.jsonify(data)

    return app
