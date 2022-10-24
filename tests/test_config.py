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


@pytest.mark.parametrize("filename, cli_param, result", [
    ('config_recursive_on', None, True),
    ('config_recursive_off', None, False),
    ('config_recursive_on', False, False),
    ('config_recursive_off', False, False),
    ('config_recursive_on', True, True),
    ('config_recursive_off', True, True),
    ('config_stub', None, False),
    ('config_stub', True, True),
    ('config_stub', False, False),
])
def test_config_recursive(filename, cli_param, result):
    config = Config(config_file_name=str(DATA / f'{filename}.yaml'), recursive=cli_param)
    assert config.recursive == result


@pytest.mark.parametrize("filename, deps, deps_lock, result_deps, result_deps_lock", [
    ('config_deps', "", "", "test1_dependencies.txt", "test1_dependencies.txt.lock"),
    ('config_depslock', "", "", "dependencies.txt", "test2_dependencies.txt.lock"),
    ('config_deps_depslock', "", "", "test3_dependencies.txt", "test4_dependencies.txt.lock"),
    ('config_stub', "", "", "dependencies.txt", "dependencies.txt.lock"),
    ('config_deps', "derps.txt", "", "derps.txt", "derps.txt.lock"),
    ('config_depslock', "derps.txt", "", "derps.txt", "derps.txt.lock"),
    ('config_deps_depslock', "derps.txt", "", "derps.txt", "derps.txt.lock"),
    ('config_stub', "derps.txt", "", "derps.txt", "derps.txt.lock"),
    ('config_deps', "", "derps.txt.lock", "test1_dependencies.txt", "derps.txt.lock"),
    ('config_depslock', "", "derps.txt.lock", "dependencies.txt", "derps.txt.lock"),
    ('config_deps_depslock', "", "derps.txt.lock", "test3_dependencies.txt", "derps.txt.lock"),
    ('config_stub', "derps.txt", "derps.txt.lock", "derps.txt", "derps.txt.lock"),
    ('config_deps', "derps.txt", "derps.txt.lock", "derps.txt", "derps.txt.lock"),
    ('config_depslock', "derps.txt", "derps.txt.lock", "derps.txt", "derps.txt.lock"),
    ('config_deps_depslock', "derps.txt", "derps.txt.lock", "derps.txt", "derps.txt.lock"),
    ('config_stub', "derps.txt", "derps.txt.lock", "derps.txt", "derps.txt.lock"),
])
def test_config_deps_depslock(filename, deps, deps_lock, result_deps, result_deps_lock):
    config = Config(config_file_name=str(DATA / f'{filename}.yaml'), deps_file_path=deps, deps_lock_file_path=deps_lock)
    assert config.deps_file_name == result_deps
    assert config.deps_lock_file_name == result_deps_lock
