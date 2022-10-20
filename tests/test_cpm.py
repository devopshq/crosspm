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
