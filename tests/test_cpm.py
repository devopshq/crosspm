# -*- coding: utf-8 -*-
import json
import os
import subprocess

from docopt import docopt
import logging
import pytest
import crosspm
from crosspm.cpm import App
from crosspm.helpers.config import CROSSPM_DEPENDENCY_LOCK_FILENAME


class TestCpm:
    def setup_class(self):
        print("\n=== TestCpm - setup class ===\n")

    def teardown_class(self):
        print("\n=== TestCpm - teardown class ===\n")

    def setup(self):
        print("TestCpm - setup method")

    def teardown(self):
        print("TestCpm - teardown method")

    def test_add(self):
        assert 2 + 2 == 4

    def test_mul(self):
        assert 3 * 3 == 9

    def test_check_common_args(self):
        test = {'--config': 'D:/crosspm-1/tests/crosspm.yaml','--depslock-path': './cpm.manifest','--help': False,'--options': 'contract=R11.0,quality=stable,os=linux','--out-format': 'stdout',
         '--out-prefix': '',
         '--output': None,
         '--verbose': True,
         '--verbosity': '30',
         '--version': False,
         '<OUT>': None,
         '<SOURCE>': None,
         'download': True,
         'pack': False,
         'promote': False}

        arguments = docopt(test, argv=test,version='0.8.1')

        app = App(arguments)
        assert App.check_common_args()