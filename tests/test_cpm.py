# -*- coding: utf-8 -*-
import os

import pytest

from crosspm.cpm import CrossPM


#
# ARGS parse
#

@pytest.mark.parametrize("expect, raw", [

    (["command", "--config", "/home/src/config.yml"],
     "command --config /home/src/config.yml"),

    (["command"],
     "command"),

    (["command", "--command", "my", "args"],
     "command --command my args"),

    (["command", "--recursive=True"],
     "command --recursive"),

    (["command", "--recursive=True", "--other", "command"],
     "command --recursive --other command"),

    (["command", "--recursive=True"],
     "command --recursive=True"),

    (["command", "--recursive=False"],
     "command --recursive=False"),

    (["command", "--recursive", "True"],
     "command --recursive True"),

    (["command", "--recursive", "False"],
     "command --recursive False"),

    (["command", "--recursive", "false"],
     "command --recursive false"),

])
def test_prepare_args_any(expect, raw):
    assert CrossPM.prepare_args(raw, windows=False) == expect, "Error when pass as string, on Linux-system"
    assert CrossPM.prepare_args(raw, windows=True) == expect, "Error when pass as string, on Windows-system"


@pytest.mark.parametrize("expect, raw", [
    (["command", "--config", "e:\\project\\config.yaml"],
     "command --config e:\\project\\config.yaml"),
    (['download', '--options', '"with quotes"'],
     'download --options "with quotes"'),
])
def test_prepare_args_windows(expect, raw):
    assert CrossPM.prepare_args(raw, windows=True) == expect, "Error when pass as string, on Windows-system"


@pytest.mark.parametrize("expect, raw", [
    (['download', '--options', 'with quotes'],
     'download --options "with quotes"'),
])
def test_prepare_args_linux(expect, raw):
    assert CrossPM.prepare_args(raw, windows=False) == expect, "Error when pass as string, on Linux-system"


#
# DOWNLOAD
#

def test_download_recursive_default():
    cpm = CrossPM("download")
    assert cpm.recursive is True


def test_download_recursive():
    cpm = CrossPM("download --recursive")
    assert cpm.recursive is True


def test_download_recursive_false():
    cpm = CrossPM("download --recursive False")
    assert cpm.recursive is False


def test_download_recursive_true():
    cpm = CrossPM("download --recursive True")
    assert cpm.recursive is True


#
# LOCK
#

def test_lock_recursive_default():
    cpm = CrossPM("lock")
    assert cpm.recursive is False


def test_lock_recursive():
    cpm = CrossPM("lock --recursive")
    assert cpm.recursive is True


def test_lock_recursive_true():
    cpm = CrossPM("lock --recursive True")
    assert cpm.recursive is True


def test_lock_recursive_false():
    cpm = CrossPM("lock --recursive False")
    assert cpm.recursive is False


def test_lock_recursive_unknown():
    try:
        _ = CrossPM("lock --recursive Trololo")
    except Exception as e:
        assert "Trololo" in str(e)


# --stdout

def test_stdout_flag():
    cpm = CrossPM("download")
    assert cpm.stdout is False

    cpm = CrossPM("download --stdout")
    assert cpm.stdout is True

    os.environ['CROSSPM_STDOUT'] = '1'
    cpm = CrossPM("download")
    assert cpm.stdout is True

