# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# isort:skip_file
from datetime import datetime

import tests.integration_tests.test_app  # noqa: F401
from superset.dataframe import df_to_records
from superset.db_engine_specs import BaseEngineSpec
from superset.result_set import dedup, SupersetResultSet
from superset.utils.core import GenericDataType

from .base_tests import SupersetTestCase


class TestSupersetResultSet(SupersetTestCase):
    def test_dedup(self):
        assert dedup(["foo", "bar"]) == ["foo", "bar"]
        assert dedup(["foo", "bar", "foo", "bar", "Foo"]) == [
            "foo",
            "bar",
            "foo__1",
            "bar__1",
            "Foo",
        ]
        assert dedup(["foo", "bar", "bar", "bar", "Bar"]) == [
            "foo",
            "bar",
            "bar__1",
            "bar__2",
            "Bar",
        ]
        assert dedup(["foo", "bar", "bar", "bar", "Bar"], case_sensitive=False) == [
            "foo",
            "bar",
            "bar__1",
            "bar__2",
            "Bar__3",
        ]

    def test_get_columns_basic(self):
        data = [("a1", "b1", "c1"), ("a2", "b2", "c2")]
        cursor_descr = (("a", "string"), ("b", "string"), ("c", "string"))
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns == [
            {
                "is_dttm": False,
                "type": "STRING",
                "type_generic": GenericDataType.STRING,
                "column_name": "a",
                "name": "a",
            },
            {
                "is_dttm": False,
                "type": "STRING",
                "type_generic": GenericDataType.STRING,
                "column_name": "b",
                "name": "b",
            },
            {
                "is_dttm": False,
                "type": "STRING",
                "type_generic": GenericDataType.STRING,
                "column_name": "c",
                "name": "c",
            },
        ]

    def test_get_columns_with_int(self):
        data = [("a1", 1), ("a2", 2)]
        cursor_descr = (("a", "string"), ("b", "int"))
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns == [
            {
                "is_dttm": False,
                "type": "STRING",
                "type_generic": GenericDataType.STRING,
                "column_name": "a",
                "name": "a",
            },
            {
                "is_dttm": False,
                "type": "INT",
                "type_generic": GenericDataType.NUMERIC,
                "column_name": "b",
                "name": "b",
            },
        ]

    def test_get_columns_type_inference(self):
        data = [
            (1.2, 1, "foo", datetime(2018, 10, 19, 23, 39, 16, 660000), True),
            (3.14, 2, "bar", datetime(2019, 10, 19, 23, 39, 16, 660000), False),
        ]
        cursor_descr = (("a", None), ("b", None), ("c", None), ("d", None), ("e", None))
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns == [
            {
                "is_dttm": False,
                "type": "FLOAT",
                "type_generic": GenericDataType.NUMERIC,
                "column_name": "a",
                "name": "a",
            },
            {
                "is_dttm": False,
                "type": "INT",
                "type_generic": GenericDataType.NUMERIC,
                "column_name": "b",
                "name": "b",
            },
            {
                "is_dttm": False,
                "type": "STRING",
                "type_generic": GenericDataType.STRING,
                "column_name": "c",
                "name": "c",
            },
            {
                "is_dttm": True,
                "type": "DATETIME",
                "type_generic": GenericDataType.TEMPORAL,
                "column_name": "d",
                "name": "d",
            },
            {
                "is_dttm": False,
                "type": "BOOL",
                "type_generic": GenericDataType.BOOLEAN,
                "column_name": "e",
                "name": "e",
            },
        ]

    def test_is_date(self):
        data = [("a", 1), ("a", 2)]
        cursor_descr = (("a", "string"), ("a", "string"))
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.is_temporal("DATE") is True
        assert results.is_temporal("DATETIME") is True
        assert results.is_temporal("TIME") is True
        assert results.is_temporal("TIMESTAMP") is True
        assert results.is_temporal("STRING") is False
        assert results.is_temporal("") is False
        assert results.is_temporal(None) is False

    def test_dedup_with_data(self):
        data = [("a", 1), ("a", 2)]
        cursor_descr = (("a", "string"), ("a", "string"))
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        column_names = [col["column_name"] for col in results.columns]
        self.assertListEqual(column_names, ["a", "a__1"])  # noqa: PT009

    def test_int64_with_missing_data(self):
        data = [(None,), (1239162456494753670,), (None,), (None,), (None,), (None,)]
        cursor_descr = [("user_id", "bigint", None, None, None, None, True)]
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns[0]["type"] == "BIGINT"
        assert results.columns[0]["type_generic"] == GenericDataType.NUMERIC

    def test_data_as_list_of_lists(self):
        data = [[1, "a"], [2, "b"]]
        cursor_descr = [
            ("user_id", "INT", None, None, None, None, True),
            ("username", "STRING", None, None, None, None, True),
        ]
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        df = results.to_pandas_df()
        assert df_to_records(df) == [
            {"user_id": 1, "username": "a"},
            {"user_id": 2, "username": "b"},
        ]

    def test_nullable_bool(self):
        data = [(None,), (True,), (None,), (None,), (None,), (None,)]
        cursor_descr = [("is_test", "bool", None, None, None, None, True)]
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns[0]["type"] == "BOOL"
        assert results.columns[0]["type_generic"] == GenericDataType.BOOLEAN
        df = results.to_pandas_df()
        assert df_to_records(df) == [
            {"is_test": None},
            {"is_test": True},
            {"is_test": None},
            {"is_test": None},
            {"is_test": None},
            {"is_test": None},
        ]

    def test_nested_types(self):
        data = [
            (
                4,
                [{"table_name": "unicode_test", "database_id": 1}],
                [1, 2, 3],
                {"chart_name": "scatter"},
            ),
            (
                3,
                [{"table_name": "birth_names", "database_id": 1}],
                [4, 5, 6],
                {"chart_name": "plot"},
            ),
        ]
        cursor_descr = [("id",), ("dict_arr",), ("num_arr",), ("map_col",)]
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns[0]["type"] == "INT"
        assert results.columns[0]["type_generic"] == GenericDataType.NUMERIC
        assert results.columns[1]["type"] == "STRING"
        assert results.columns[1]["type_generic"] == GenericDataType.STRING
        assert results.columns[2]["type"] == "STRING"
        assert results.columns[2]["type_generic"] == GenericDataType.STRING
        assert results.columns[3]["type"] == "STRING"
        assert results.columns[3]["type_generic"] == GenericDataType.STRING
        df = results.to_pandas_df()
        assert df_to_records(df) == [
            {
                "id": 4,
                "dict_arr": '[{"table_name": "unicode_test", "database_id": 1}]',
                "num_arr": "[1, 2, 3]",
                "map_col": "{'chart_name': 'scatter'}",
            },
            {
                "id": 3,
                "dict_arr": '[{"table_name": "birth_names", "database_id": 1}]',
                "num_arr": "[4, 5, 6]",
                "map_col": "{'chart_name': 'plot'}",
            },
        ]

    def test_single_column_multidim_nested_types(self):
        data = [
            (
                [
                    "test",
                    [
                        [
                            "foo",
                            123456,
                            [
                                [["test"], 3432546, 7657658766],
                                [["fake"], 656756765, 324324324324],
                            ],
                        ]
                    ],
                    ["test2", 43, 765765765],
                    None,
                    None,
                ],
            )
        ]
        cursor_descr = [("metadata",)]
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns[0]["type"] == "STRING"
        assert results.columns[0]["type_generic"] == GenericDataType.STRING
        df = results.to_pandas_df()
        assert df_to_records(df) == [
            {
                "metadata": '["test", [["foo", 123456, [[["test"], 3432546, 7657658766], [["fake"], 656756765, 324324324324]]]], ["test2", 43, 765765765], null, null]'  # noqa: E501
            }
        ]

    def test_nested_list_types(self):
        data = [([{"TestKey": [123456, "foo"]}],)]
        cursor_descr = [("metadata",)]
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns[0]["type"] == "STRING"
        assert results.columns[0]["type_generic"] == GenericDataType.STRING
        df = results.to_pandas_df()
        assert df_to_records(df) == [{"metadata": '[{"TestKey": [123456, "foo"]}]'}]

    def test_empty_datetime(self):
        data = [(None,)]
        cursor_descr = [("ds", "timestamp", None, None, None, None, True)]
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns[0]["type"] == "TIMESTAMP"
        assert results.columns[0]["type_generic"] == GenericDataType.TEMPORAL

    def test_no_type_coercion(self):
        data = [("a", 1), ("b", 2)]
        cursor_descr = [
            ("one", "varchar", None, None, None, None, True),
            ("two", "int", None, None, None, None, True),
        ]
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns[0]["type"] == "VARCHAR"
        assert results.columns[0]["type_generic"] == GenericDataType.STRING
        assert results.columns[1]["type"] == "INT"
        assert results.columns[1]["type_generic"] == GenericDataType.NUMERIC

    def test_empty_data(self):
        data = []
        cursor_descr = [
            ("emptyone", "varchar", None, None, None, None, True),
            ("emptytwo", "int", None, None, None, None, True),
        ]
        results = SupersetResultSet(data, cursor_descr, BaseEngineSpec)
        assert results.columns == []
