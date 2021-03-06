# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from crosspm.helpers.config import Config

DATA = Path(__file__).parent / 'data'


@pytest.mark.parametrize("filename", [
    ('config_en_cp1251'),
    ('config_en_utf8_bom'),
    ('config_ru_utf8_bom'),
])
def test_config(filename):
    c = Config.load_yaml(str(DATA / '{}.yaml'.format(filename)))
    assert isinstance(c, dict)


@pytest.mark.parametrize("filename", [
    ('config_import_without_comment'),
    ('config_import_with_comment'),
])
def test_config_comment_before_import_handle(filename, monkeypatch):
    monkeypatch.chdir('{}/data'.format(Path(__file__).parent))
    result = Config.load_yaml(str(DATA / '{}.yaml'.format(filename)))
    assert '.aliases' in result
