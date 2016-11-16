# -*- coding: utf-8 -*-

import pytest
import sys
import traceback

from crosspm.cpm import CrossPM


class TestCpm:
    def setup_class(self):
        print("\n=== TestCpm - setup class ===\n")

    def teardown_class(self):
        print("\n=== TestCpm - teardown class ===\n")

    def setup(self):
        print("TestCpm - setup method")

    def teardown(self):
        print("TestCpm - teardown method")

    def test_read_config_without_configfile(self):
        print("\ttest_read_config_without_configfile")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, 'download')
        app = CrossPM()
        app.read_config()

    def test_read_config_without_configfile_2(self):
        print("\ttest_read_config_without_configfile_2")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, 'download')
        sys.argv.insert(2, '-o contract=R11.0,quality=stable,os=linux')
        app = CrossPM()
        app.read_config()

    def test_check_common_args_with_verbose(self):
        print("\ttest_check_common_args_with_verbose")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, 'download')
        sys.argv.insert(2, '--verbose')
        app = CrossPM()
        app.check_common_args()

    def test_check_common_args_with_verbose_2(self):
        print("\ttest_check_common_args_with_verbose_2")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, 'download')
        sys.argv.insert(2, '--out-format=stdout')
        sys.argv.insert(3, '--depslock-path=./tests/pt/cpm.manifest')
        sys.argv.insert(4, '-o contract=R11.0, quality=stable, os=linux')
        sys.argv.insert(5, '--verbose')
        app = CrossPM()
        try:
            app.check_common_args()
        except SystemExit as e:
            if e.code == None:
                assert True
            else:
                assert False

    def test_argv_help_false(self):
        print("\ttest_argv_help_false")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, '---help')
        try:
            app = CrossPM()
        except SystemExit as e:
            if e.code == None:
                assert True
            else:
                assert False

    def test_argv_h_false(self):
        print("\ttest_argv_h_false")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, '--h')
        try:
            app = CrossPM()
        except SystemExit as e:
            if e.code == None:
                assert True
            else:
                assert "false"

    def test_read_config_with_configfile(self):
        print("\ttest_read_config_with_configfile")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, 'download')
        sys.argv.insert(2, '--config=D:/crosspm-1/tests/crosspm.yaml')
        app = CrossPM()
        app.read_config()

    def test_read_config_with_configfile_2(self):
        print("\ttest_read_config_with_configfile_2")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, 'download')
        sys.argv.insert(2, '--depslock-path=D:/crosspm-1/tests/cpm.manifest')
        sys.argv.insert(3, '--config=D:/crosspm-1/tests/pt/crosspm.yaml')
        sys.argv.insert(4, '-o contract=R11.0,quality=stable,os=linux')
        app = CrossPM()
        app.read_config()

    def test_check_common_args_without_verbose(self):
        print("\ttest_check_common_args_without_verbose")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, 'download')
        app = CrossPM()
        app.check_common_args()

    def test_check_common_args_without_verbose_2(self):
        print("\ttest_check_common_args_without_verbose")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, 'download')
        sys.argv.insert(2, '--out-format=stdout')
        sys.argv.insert(3, '--depslock-path=./tests/pt/cpm.manifest')
        sys.argv.insert(4, '-o contract=R11.0, quality=stable, os=linux')
        app = CrossPM()
        app.check_common_args()

    def test_argv_help(self):
        print("\ttest_argv_help")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, '--help')
        try:
            app = CrossPM()
        except SystemExit as e:
            if e.code == None:
                assert True
            else:
                assert False

    def test_argv_h(self):
        print("\ttest_argv_h")
        sys.argv.clear()
        sys.argv.append(1)
        sys.argv.insert(1, '-h')
        try:
            app = CrossPM()
        except SystemExit as e:
            if e.code == None:
                assert True
            else:
                assert False
