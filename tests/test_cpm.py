# -*- coding: utf-8 -*-
import pytest

from crosspm.cpm import CrossPM


#
# ARGS parse
#

@pytest.mark.parametrize("expect, raw", [
    (['download', '--options', 'with quotes'],
     'download --options "with quotes"'),

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
def test_prepare_args(expect, raw):
    assert CrossPM.prepare_args(raw) == expect, "Error when pass as string"


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
        cpm = CrossPM("lock --recursive Trololo")
    except Exception as e:
        assert "Trololo" in str(e)
