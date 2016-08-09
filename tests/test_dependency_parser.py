# -*- coding: utf-8 -*-
import pytest

from crosspm.helpers.dependency_parser import (
    _dependency_contracts_dict,
    DependencyParserException,
    DependencyBase,
    DependencyContractSimple,
    DependencyContractQualityV1,
    DependencyParser,
)


def test_issubclass():
    assert issubclass(DependencyParserException, Exception)
    assert issubclass(DependencyContractSimple, DependencyBase)
    assert issubclass(DependencyContractQuality_1, DependencyBase)


def test_create():
    assert isinstance(DependencyBase.create(), DependencyBase)
    assert isinstance(DependencyContractSimple.create(), DependencyContractSimple)
    assert isinstance(DependencyContractQuality_1.create(), DependencyContractQuality_1)


def test_dependency_base():
    with pytest.raises(RuntimeError):
        DependencyBase().parse_string('')


def test_contract_name():
    assert _dependency_contracts_dict == {
        'simple': DependencyContractSimple,
        'quality:1': DependencyContractQuality_1,
    }


def test_dependency_parser_is():
    assert DependencyParser('simple')._is_empty('')
    assert not DependencyParser('simple')._is_empty(' ')

    assert DependencyParser('simple')._is_command('--')
    assert not DependencyParser('simple')._is_command(' --')


def test_dependency_parser_set_dep_contract():
    with pytest.raises(KeyError) as e:
        DependencyParser('simple')._set_dep_contract('some value')


def test_dependency_parser_parsecmd():
    with pytest.raises(DependencyParserException) as e:
        DependencyParser('simple')._parseCmd('--pragma')

    assert 'wrong syntax for command expression' == str(e.value)

    with pytest.raises(DependencyParserException) as e:
        DependencyParser('simple')._parseCmd('--pragma=aa')

    assert 'unknown command PRAGMA' == str(e.value)


def test_dependency_parser_parse_cmd_contact():
    with pytest.raises(DependencyParserException) as e:
        DependencyParser('simple')._parse_cmd_contact('CONTRACT', '')

    assert 'command CONTRACT requires value' == str(e.value)

    with pytest.raises(DependencyParserException) as e:
        DependencyParser('simple')._parse_cmd_contact('CONTRACT', '1')

    assert 'incorrect value 1 for command CONTRACT' == str(e.value)


def test_dependency_parser_dep_contract_a():
    x = DependencyParser('simple')
    assert isinstance(x._DependencyParser__dep_contract(), DependencyContractSimple)

    x._parse_cmd_contact('CONTRACT', 'simple')
    assert isinstance(x._DependencyParser__dep_contract(), DependencyContractSimple)

    x._parse_cmd_contact('CONTRACT', 'quality:1')
    assert isinstance(x._DependencyParser__dep_contract(), DependencyContractQualityV1)


def test_dependency_parser_set_dep_contract_b():
    with pytest.raises(KeyError) as e:
        DependencyParser('simple')._set_dep_contract('zzz')


def test_incorrect_contact_simple():
    with pytest.raises(DependencyParserException) as e:
        DependencyParser('simple').parse(('-',))

    assert 'not enought arguments' == str(e.value)

    with pytest.raises(DependencyParserException) as e:
        DependencyParser('simple').parse(('- -',))

    assert 'not enought arguments' == str(e.value)

    with pytest.raises(DependencyParserException) as e:
        DependencyParser('simple').parse(('- - - -',))

    assert 'too much arguments' == str(e.value)


def test_incorrect_contact_quality_v1():
    with pytest.raises(DependencyParserException) as e:
        DependencyParser('simple').parse(
            '--contract=quality:1\n- - - -'.split('\n')
        )

    assert 'not enought arguments' == str(e.value)

    with pytest.raises(DependencyParserException) as e:
        DependencyParser('simple').parse(
            '--contract=quality:1\n- - - - - -'.split('\n')
        )

    assert 'too much arguments' == str(e.value)


def test_dependency_parser():
    source = """
    # some comments
    a * b
    --contract=quality:1
    b * - a b
    --contract=simple
    c * branch
    """

    deps = DependencyParser('simple').parse(source.split('\n'))

    assert all(filter(
        lambda x: isinstance(*x),
        zip(
            deps,
            (
                DependencyContractSimple,
                DependencyContractQuality_1,
                DependencyContractSimple,
            ))))

    assert list(map(lambda x: x.package_params(), deps)) == [
        ('a', '*', 'b'),
        ('b', '*', None, 'a', 'b'),
        ('c', '*', 'branch'),
    ]


def test_dependency_parser_stripcomments():
    parser = DependencyParser('simple')

    a = ['', ' ', ' da/ta ', ' data #aaa ', ' data2#aaa ', ' #aaa ', '#']
    b = ['', ' ', ' da/ta ', ' data //aaa ', ' data2//aaa ', ' //aaa ', '//']
    c = ['', '', 'da/ta', 'data', 'data2', '', '']

    assert list(map(parser._strip_comments, a)) == c

    parser.SYMBOL_COMMENT = '//'

    assert list(map(parser._strip_comments, b)) == c
