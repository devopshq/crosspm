# -*- coding: utf-8 -*-
import pytest

from crosspm.adapters.artifactoryaql import Adapter
from crosspm.helpers.source import Source


class TestAdapter:
    @pytest.fixture()
    def source(self):
        source = Source("", "", {})
        return source

    @pytest.fixture()
    def auth(self):
        list_or_file_path = {'raw': [{'auth': 'concrete_user:concrete_password'}]}
        return list_or_file_path

    @pytest.fixture()
    def user_password(self):
        list_or_file_path = {'raw': [{'user': 'concrete_user', 'password': 'concrete_password'}]}
        return list_or_file_path

    def test_split_auth(self):
        assert ['concrete_user', 'concrete_password'] == Adapter("").split_auth('concrete_user:concrete_password')

    def test_search_auth_with_auth_parameter(self, source, auth):
        source.args['auth'] = '{auth}'
        Adapter("").search_auth(auth, source)
        assert source.args['auth'] == ['concrete_user', 'concrete_password']

    def test_search_auth_with_user_password_parameter(self, source, user_password):
        source.args['auth'] = '{user}:{password}'
        Adapter("").search_auth(user_password, source)
        assert source.args['auth'] == ['concrete_user', 'concrete_password']

    def test_search_auth_with_password_parameter(self, source, user_password):
        source.args['auth'] = 'concrete_user:{password}'
        Adapter("").search_auth(user_password, source)
        assert source.args['auth'] == ['concrete_user', 'concrete_password']

    def test_search_auth_without_parameter(self, source, user_password):
        source.args['auth'] = 'concrete_user:concrete_password'
        Adapter("").search_auth(user_password, source)
        assert source.args['auth'] == ['concrete_user', 'concrete_password']
