# -*- coding: utf-8 -*-
import os

from crosspm.helpers.python import get_object_from_string


def test_get_object_from_string():
    obj_ = get_object_from_string('os.path')
    assert os.path is obj_
