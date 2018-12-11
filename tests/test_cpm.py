# -*- coding: utf-8 -*-

from crosspm.cpm import CrossPM


#
# DOWNLOAD
#

def test_download_recursive_default():
    cpm = CrossPM("download")
    assert cpm.recursive is True


def test_download_recursive():
    cpm = CrossPM("download --recursive")
    assert cpm.recursive is True


def test_download_recursive_False():
    cpm = CrossPM("download --recursive False")
    assert cpm.recursive is False


def test_download_recursive_True():
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


def test_lock_recursive_True():
    cpm = CrossPM("lock --recursive True")
    assert cpm.recursive is True


def test_lock_recursive_False():
    cpm = CrossPM("lock --recursive False")
    assert cpm.recursive is False
