# -*- coding: utf-8 -*-

import pytest
import sys
import traceback
from crosspm.cpm import App


class TestCpm:
    def setup_class(self):
        print("\n=== TestCpm - setup class ===\n")

    def teardown_class(self):
        print("\n=== TestCpm - teardown class ===\n")

    def setup(self):
        print("TestCpm - setup method")

    def teardown(self):
        print("TestCpm - teardown method")

    # def test_check_common_args(self):
    #     sys.argv.clear()
    #     sys.argv.append(1)
    #     sys.argv.insert(1,'--help')
    #     argv = sys.argv[1:]
    #     try:
    #         app = App().__init__(argv)
    #     except SystemExit as e:
    #         DebugMsg("Execute command: {}".format(e))
    #         print("App__init__")
    #     assert App.check_common_args()

    def test_argv_help(self):
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, '---help')
        argv = sys.argv[1:]
        try:
            app = App().__init__(argv)
        except SystemExit as e:
            if e.code == None:
                assert True
            else:
                assert False

    #     sys.argv.clear()
    #     sys.argv.append(1)
    #     sys.argv.insert(1, '-help')
    #     argv = sys.argv[1:]
    #     try:
    #         app = App().__init__(argv)
    #     except SystemExit as e:
    #         assert True
    #
    # def test_argv_h(self):
    #     sys.argv.clear()
    #     sys.argv.append(1)
    #     sys.argv.insert(1, '-h')
    #     argv = sys.argv[1:]
    #     try:
    #         app = App().__init__(argv)
    #     except SystemExit as e:
    #         assert True
    #
    #     sys.argv.clear()
    #     sys.argv.append(1)
    #     sys.argv.insert(1, '--h')
    #     argv = sys.argv[1:]
    #     try:
    #         app = App().__init__(argv)
    #     except SystemExit as e:
    #         assert True





# test = {'--config': 'D:/crosspm-1/tests/crosspm.yaml', '--depslock-path': './cpm.manifest', '--help': False,
#         '--options': 'contract=R11.0,quality=stable,os=linux', '--out-format': 'stdout',
#         '--out-prefix': '',
#         '--output': None,
#         '--verbose': True,
#         '--verbosity': '30',
#         '--version': False,
#         '<OUT>': None,
#         '<SOURCE>': None,
#         'download': True,
#         'pack': False,
#         'promote': False}

# def test_add(self):
    #     assert 2 + 2 == 4
    #
    # def test_mul(self):
    #     assert 3 * 3 == 9