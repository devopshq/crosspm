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
