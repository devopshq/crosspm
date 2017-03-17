# -*- coding: utf-8 -*-
import pytest
import yaml
from . import BaseParserTest, assert_warn
from crosspm.helpers.parser import Parser


class TestParser(BaseParserTest):
    config = """
    parsers:
      common:
        columns:
          version: "{int}.{int}.{int}[.{int}][-{str}]"
        sort:
          - version
          - '*'
        index: -1

      artifactory:
        path: "{server}/{repo}/{package}/{branch}/{version}/{compiler|any}/{arch|any}/{osname}/{package}.{version}[.zip|.tar.gz|.nupkg]"
        properties: ""
    """

    @pytest.fixture(scope='class', autouse=True)
    def init(self):
        config = yaml.safe_load(self.config)
        assert self.init_parser(config.get('parsers', {})) is True

    def test__init(self):
        assert isinstance(self._parsers.get('artifactory', None), Parser)

    def test__parse_by_mask__package(self):
        parser = self._parsers.get('artifactory', None)

        assert \
            parser.parse_by_mask('package', 'boost', False, True) == \
            'boost'

    def test__parse_by_mask__version(self):
        parser = self._parsers.get('artifactory', None)
        assert \
            parser.parse_by_mask('version', '1.2.3', False, True) == \
            ['1', '2', '3', None, None]

        assert \
            parser.parse_by_mask('version', '1.2.3.4', False, True) == \
            ['1', '2', '3', '4', None]

        assert \
            parser.parse_by_mask('version', '1.2.3.4-feature', False, True) == \
            ['1', '2', '3', '4', 'feature']

        # TODO: Make this test pass
        assert_warn(
            parser.parse_by_mask('version', '1.2.3-feature', False, True),
            "=="
            "['1', '2', '3', None, 'feature']"
        )

    def test__parse_by_mask__version_with_types(self):
        parser = self._parsers.get('artifactory', None)
        assert \
            parser.parse_by_mask('version', '1.2.3', True, True) == \
            [('1', 'int'), ('2', 'int'), ('3', 'int'), (None, 'int'), (None, 'str')]

        assert \
            parser.parse_by_mask('version', '1.2.3.4', True, True) == \
            [('1', 'int'), ('2', 'int'), ('3', 'int'), ('4', 'int'), (None, 'str')]

        assert \
            parser.parse_by_mask('version', '1.2.3.4-feature', True, True) == \
            [('1', 'int'), ('2', 'int'), ('3', 'int'), ('4', 'int'), ('feature', 'str')]

        # TODO: Make this test pass
        assert_warn(
            parser.parse_by_mask('version', '1.2.3-feature', True, True),
            "=="
            "[('1', 'int'), ('2', 'int'), ('3', 'int'), (None, 'int'), ('feature', 'str')]"
        )

    def test__merge_with_mask(self):
        pass

    @pytest.mark.artifactoryaql
    def test_split_fixed_pattern_with_file_name_with_mask(self):
        parser = self._parsers.get('common', None)

        path = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/boost/1.60-pm/*.*.*/vc110/x86/win/boost.*.*.*.tar.gz"
        path_fixed = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/boost/1.60-pm"
        path_pattern = "*.*.*/vc110/x86/win"
        file_name_pattern = "boost.*.*.*.tar.gz"


        _path_fixed, _path_pattern, _file_name_pattern = parser.split_fixed_pattern_with_file_name(path)

        assert path_fixed == _path_fixed
        assert path_pattern == _path_pattern
        assert file_name_pattern == _file_name_pattern

    @pytest.mark.artifactoryaql
    def test_split_fixed_pattern_with_file_name_with_lock(self):
        parser = self._parsers.get('common', None)

        path = "https://repo.ptsecurity.ru/artifactory/libs-cpp-release.snapshot/zlib/1.2.8-pm/1.2.8.199/vc110/x86/win/zlib.1.2.8.199.tar.gz"
        path_fixed = "https://repo.ptsecurity.ru/artifactory/libs-cpp-release.snapshot/zlib/1.2.8-pm/1.2.8.199/vc110/x86/win"
        path_pattern = ""
        file_name_pattern = "zlib.1.2.8.199.tar.gz"


        _path_fixed, _path_pattern, _file_name_pattern = parser.split_fixed_pattern_with_file_name(path)

        assert path_fixed == _path_fixed
        assert path_pattern == _path_pattern
        assert file_name_pattern == _file_name_pattern
