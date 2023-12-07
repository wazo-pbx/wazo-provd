# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import unittest
from typing import Any

import pytest
from hamcrest import (
    all_of,
    assert_that,
    equal_to,
    has_entries,
    is_,
    none,
    not_,
    starts_with,
)
from pydantic import ValidationError

from ..config import (
    DefaultConfigFactory,
    _remove_none_values,
    ConfigSchema,
    RawConfigSchema,
)


def test_config_schema_empty() -> None:
    with pytest.raises(ValidationError) as exc_trace:
        ConfigSchema()

    error = exc_trace.value
    assert isinstance(error, ValidationError)
    assert error.errors() == [
        {'loc': ('id',), 'msg': 'field required', 'type': 'value_error.missing'},
        {
            'loc': ('parent_ids',),
            'msg': 'field required',
            'type': 'value_error.missing',
        },
        {
            'loc': ('raw_config',),
            'msg': 'field required',
            'type': 'value_error.missing',
        },
        {'loc': ('transient',), 'msg': 'field required', 'type': 'value_error.missing'},
    ]


def test_raw_config_schema_missing_values() -> None:
    with pytest.raises(ValidationError) as exc_trace:
        RawConfigSchema(sip_lines={'1': {'username': 'test_username'}})

    error = exc_trace.value
    assert isinstance(error, ValidationError)
    assert error.errors() == [
        {'loc': ('ip',), 'msg': 'field required', 'type': 'value_error.missing'},
        {
            'loc': ('sip_lines', '1', 'password'),
            'msg': 'field required',
            'type': 'value_error.missing',
        },
        {
            'loc': ('sip_lines', '1', 'display_name'),
            'msg': 'field required',
            'type': 'value_error.missing',
        },
        {
            'loc': ('__root__',),
            'msg': 'You must define either `tftp_port` or `http_port`.',
            'type': 'value_error',
        },
    ]


def test_raw_config_valid() -> None:
    sip_line_1 = {
        'username': 'test_username',
        'password': 'a-password',
        'display_name': 'name',
    }
    values = {
        'ip': 'localhost',
        'http_port': '443',
        'sip_lines': {'1': sip_line_1},
    }
    config = RawConfigSchema(**values)
    assert sip_line_1.items() <= config.dict()['sip_lines']['1'].items()


@pytest.fixture(name='default_config_factory')
def default_config_factory_fixture() -> DefaultConfigFactory:
    return DefaultConfigFactory()


def test_sip_line(default_config_factory: DefaultConfigFactory) -> None:
    config: dict[str, Any] = {'raw_config': {}}
    result = default_config_factory(config)
    assert_that(result, is_(none()))


def test_with_a_valid_sip_configuration(
    default_config_factory: DefaultConfigFactory,
) -> None:
    id_ = 'ap'
    username = 'anonymous'
    config = {
        'id': id_,
        'raw_config': {
            'sip_lines': {
                '1': {
                    'username': username,
                }
            }
        },
    }

    result = default_config_factory(config)

    assert_that(
        result,
        has_entries(
            id=all_of(
                starts_with(id_),
                not_(equal_to(id_)),
            ),
            raw_config=has_entries(
                sip_lines=has_entries(
                    '1',
                    has_entries(
                        username=username,
                    ),
                )
            ),
        ),
    )


class TestRemoveNoneValues(unittest.TestCase):
    def test_empty_dict(self) -> None:
        empty_dict: dict[str, Any] = {}
        expected_result: dict[str, Any] = {}

        result = _remove_none_values(empty_dict)
        assert_that(
            result,
            is_(equal_to(expected_result)),
        )

    def test_with_simple_dict(self) -> None:
        dict_with_nones = {
            'key1': None,
            'key2': '123',
            'key3': 123,
            'key4': False,
        }

        expected_result = {
            'key2': '123',
            'key3': 123,
            'key4': False,
        }

        result = _remove_none_values(dict_with_nones)
        assert_that(
            result,
            is_(equal_to(expected_result)),
        )

    def test_with_nested_dict(self) -> None:
        dict_with_nones = {
            'key1': {'nkey1': 123, 'nkey2': None},
        }

        expected_result = {
            'key1': {'nkey1': 123},
        }

        result = _remove_none_values(dict_with_nones)
        assert_that(
            result,
            is_(equal_to(expected_result)),
        )

    def test_with_list(self) -> None:
        dict_with_list = {
            'key1': [123, None],
        }

        expected_result = {
            'key1': [123, None],
        }

        result = _remove_none_values(dict_with_list)
        assert_that(
            result,
            is_(equal_to(expected_result)),
        )

    def test_with_dict_in_list(self) -> None:
        dict_with_list = {
            'key1': [{'nkey1': 123, 'nkey2': None}, {'nkey1': None, 'nkey2': '123'}],
        }

        expected_result = {
            'key1': [{'nkey1': 123}, {'nkey2': '123'}],
        }

        result = _remove_none_values(dict_with_list)
        assert_that(
            result,
            is_(equal_to(expected_result)),
        )
