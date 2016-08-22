# -*- coding: utf-8 -*-
import pytest

from crosspm.helpers import pm_common

# TODO: REWORK TEST COMPLETELY !!!

def test_peek_empty():
    it = (i for i in range(0))
    is_empty, first, it = pm_common.peek(it)

    assert is_empty
    assert first is None
    assert id(it) == id(it)


def test_peek_not_empty():
    is_empty, first, it = pm_common.peek(i for i in range(2))

    assert not is_empty
    assert first == 0
    assert list(it) == [0, 1]
