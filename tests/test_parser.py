# -*- coding: utf-8 -*-
import pytest
import yaml

from crosspm.helpers.parser import Parser


class BaseParserTest:
    _parsers = {}

    def init_parser(self, parsers):
        if 'common' not in parsers:
            parsers['common'] = {}
        for k, v in parsers.items():
            if k not in self._parsers:
                v.update({_k: _v for _k, _v in parsers['common'].items() if _k not in v})
                self._parsers[k] = Parser(k, v, self)
            else:
                return False
                # code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
                # msg = 'Config file contains multiple definitions of the same parser: [{}]'.format(k)
                # self._log.exception(msg)
                # raise CrosspmException(code, msg)
        if len(self._parsers) == 0:
            return False
            # code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
            # msg = 'Config file does not contain package_parsers! Unable to process any further.'
            # self._log.exception(msg)
            # raise CrosspmException(code, msg)
        return True


class TestParser(BaseParserTest):
    config = r"""
    package_parsers:
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
        usedby:
          AQL:
            "@dd.{package}.version": "{version}"
            "@dd.{package}.operator": "="
            "path":
                "$match": "*vc140/x86_64/win*"

          property-parser:
            "deb.name": "package"
            "deb.version": "version"
            "qaverdict": "qaverdict"
            
          path-parser: 'https://repo.example.com/artifactory/libs-cpp-release.snapshot/(?P<package>.*?)/(?P<branch>.*?)/(?P<version>.*?)/(?P<compiler>.*?)/(?P<arch>.*?)/(?P<osname>.*?)/.*.tar.gz'
    """

    @pytest.fixture(scope='class', autouse=True)
    def init(self):
        config = yaml.safe_load(self.config)
        assert self.init_parser(config.get('package_parsers', {})) is True

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
        # assert parser.parse_by_mask('version', '1.2.3-feature', False, True) == ['1', '2', '3', None, 'feature']

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
        # assert \
        #     parser.parse_by_mask('version', '1.2.3-feature', True, True) == \
        #     [('1', 'int'), ('2', 'int'), ('3', 'int'), (None, 'int'), ('feature', 'str')]

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

        path = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/zlib/1.2.8-pm/1.2.8.199/vc110/x86/win/zlib.1.2.8.199.tar.gz"
        path_fixed = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/zlib/1.2.8-pm/1.2.8.199/vc110/x86/win"
        path_pattern = ""
        file_name_pattern = "zlib.1.2.8.199.tar.gz"

        _path_fixed, _path_pattern, _file_name_pattern = parser.split_fixed_pattern_with_file_name(path)

        assert path_fixed == _path_fixed
        assert path_pattern == _path_pattern
        assert file_name_pattern == _file_name_pattern

    @pytest.mark.artifactoryaql
    def test_split_fixed_pattern_with_file_name_with_partial_lock(self):
        parser = self._parsers.get('common', None)

        path = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/build-tools/master/0.6.*/vc120/x86/win/build-tools.0.6.*.tar.gz"
        path_fixed = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/build-tools/master"
        path_pattern = "0.6.*/vc120/x86/win"
        file_name_pattern = "build-tools.0.6.*.tar.gz"

        _path_fixed, _path_pattern, _file_name_pattern = parser.split_fixed_pattern_with_file_name(path)

        assert path_fixed == _path_fixed
        assert path_pattern == _path_pattern
        assert file_name_pattern == _file_name_pattern

    @pytest.mark.artifactoryaql
    def test_split_fixed_pattern_with_file_name_with_masked_filename_only(self):
        parser = self._parsers.get('common', None)

        path = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/build-tools/master/vc120/x86/win/build-tools.0.6.*.tar.gz"
        path_fixed = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/build-tools/master/vc120/x86/win"
        path_pattern = ""
        file_name_pattern = "build-tools.0.6.*.tar.gz"

        _path_fixed, _path_pattern, _file_name_pattern = parser.split_fixed_pattern_with_file_name(path)

        assert path_fixed == _path_fixed
        assert path_pattern == _path_pattern
        assert file_name_pattern == _file_name_pattern

    def test_split_fixed_pattern(self):
        parser = self._parsers.get('common', None)

        path = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/boost/1.60-pm/*.*.*/vc110/x86/win/boost.*.*.*.tar.gz"
        path_fixed = "https://repo.example.com/artifactory/libs-cpp-release.snapshot/boost/1.60-pm/"
        path_pattern = "*.*.*/vc110/x86/win/boost.*.*.*.tar.gz"

        _path_fixed, _path_pattern = parser.split_fixed_pattern(path)

        assert path_fixed == _path_fixed
        assert path_pattern == _path_pattern

    def test_has_rule(self):
        parser = self._parsers.get('artifactory', None)

        assert parser.has_rule('path') is True
        assert parser.has_rule('properties') is False

    # def test_get_full_package_name(self):
    #     parser = self._parsers.get('artifactory', None)
    #
    #     package = Package('test_package', None, None, None, None, parser=parser)
    #     name = parser.get_full_package_name(package)
    #
    #     assert name == "test_package"

    def test_list_flatter(self):
        parser = self._parsers.get('common', None)

        src = [[
            'https://repo.example.com/artifactory/cybsi.snapshot/cybsi/*/*.*.*/[any|any]/[any|any]/cybsi/cybsi.*.*.*[.zip|.tar.gz|.nupkg]']]
        result = [
            'https://repo.example.com/artifactory/cybsi.snapshot/cybsi/*/*.*.*/[any|any]/[any|any]/cybsi/cybsi.*.*.*[.zip|.tar.gz|.nupkg]']

        assert parser.list_flatter(src) == result

    def test_validate_atom(self):
        parser = self._parsers.get('artifactory', None)

        assert parser.validate_atom('feature-netcore-probes', '*') is True
        assert parser.validate_atom('1.2', '>=1.3') is False

    def test_values_match(self):
        parser = self._parsers.get('artifactory', None)

        assert parser.values_match('1.3', '1.3') is True
        assert parser.values_match('2.0', '1.3') is False

    # def test_iter_matched_values(self):
    #     """
    #     module parser have no method get_values(column_name) (see line 566 in parser)
    #     so we should use mock object I think
    #     """
    #     parser = self._parsers.get('artifactory', None)
    #
    #     column_name = 'version'
    #     value = ['1', '2', '3', None]
    #
    #     ## debug
    #     #res = parser.iter_matched_values(column_name, value)
    #     #print(res)
    #
    #     assert parser.iter_matched_values('1.3', '1.3') is True

    @pytest.mark.artifactoryaql
    def test__get_params_with_extra(self):
        parser = self._parsers.get('common', None)

        vars_extra = {'path': [
            {
                'compiler': ['any'],
                'arch': ['any'],
            }
        ]}

        params = {
            'arch': 'x86',
            'compiler': 'vc140',
            'osname': 'win',
            'version': [1, 2, 3]
        }

        expected_result = [
            {
                'arch': 'x86',
                'compiler': 'vc140',
                'osname': 'win',
                'version': [1, 2, 3]
            },
            {
                'arch': 'any',
                'compiler': 'vc140',
                'osname': 'win',
                'version': [1, 2, 3]
            },
            {
                'arch': 'x86',
                'compiler': 'any',
                'osname': 'win',
                'version': [1, 2, 3]
            },
            {
                'arch': 'any',
                'compiler': 'any',
                'osname': 'win',
                'version': [1, 2, 3]
            },

        ]
        parser._rules_vars_extra = vars_extra
        result = parser.get_params_with_extra('path', params)

        for res in result:
            assert res in expected_result, "Result contain MORE element then expected"

        for res in expected_result:
            assert res in result, "Result contain LESS element then expected"

    def test_get_usedby_aql(self):
        parser = self._parsers.get('artifactory', None)  # type: Parser
        parser.merge_valued = lambda x: x  # TODO: Убрать этот грубый хак :)
        result = parser.get_usedby_aql({'package': 'packagename', 'version': '1.2.3'})
        expect_result = {
            '@dd.packagename.version': '1.2.3',
            '@dd.packagename.operator': '=',
            'path':
                {'$match': '*vc140/x86_64/win*'}
        }
        assert expect_result == result

    def test_get_usedby_aql_none(self):
        parser = self._parsers.get('common', None)  # type: Parser
        result = parser.get_usedby_aql({})
        assert result is None

    def test_get_params_from_properties(self):
        parser = self._parsers.get('artifactory', None)  # type: Parser
        params = parser.get_params_from_properties({'deb.name': 'packagename', 'deb.version': '1.2.3'})
        expect_params = {
            'package': 'packagename',
            'version': '1.2.3',
            'qaverdict': ''
        }
        assert expect_params == params

    def test_get_params_from_path(self):
        parser = self._parsers.get('artifactory', None)  # type: Parser
        params = parser.get_params_from_path(
            "https://repo.example.com/artifactory/libs-cpp-release.snapshot/zlib/1.2.8-pm/1.2.8.199/vc110/x86/win/zlib.1.2.8.199.tar.gz")
        expect_params = {
            'arch': 'x86',
            'branch': '1.2.8-pm',
            'compiler': 'vc110',
            'osname': 'win',
            'package': 'zlib',
            'version': '1.2.8.199',
        }
        assert expect_params == params
