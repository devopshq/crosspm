# -*- coding: utf-8 -*-

from pathlib import Path
import os

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
def test_config_comment_before_import_handle(filename):
    start_wd = os.getcwd()
    os.chdir(f'{Path(__file__).parent}/data')
    result = Config.load_yaml(str(DATA / '{}.yaml'.format(filename)))
    os.chdir(start_wd)
    assert '.aliases' in result
