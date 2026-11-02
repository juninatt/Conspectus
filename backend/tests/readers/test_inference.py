from datetime import UTC, date, datetime

import pytest

from conspectus.models import ColumnType, Value
from conspectus.readers.inference import Scalar, convert, infer_type


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([1, 2], ColumnType.INTEGER),
        ([1, 2.5], ColumnType.NUMBER),
        ([True, False], ColumnType.BOOLEAN),
        (["a", "b"], ColumnType.STRING),
        (["2026-10-01"], ColumnType.DATE),
        (["2026-10-01T14:30:00"], ColumnType.DATETIME),
        (["2026-10-01 14:30"], ColumnType.DATETIME),
        (["2026-10-01T14:30:00Z", "2026-10-01T15:00+02:00"], ColumnType.DATETIME),
        (["2026-10-01", "2026-10-01T14:30:00"], ColumnType.DATETIME),
        ([None, 3], ColumnType.INTEGER),
        ([None, None], ColumnType.STRING),
        ([], ColumnType.STRING),
    ],
)
def test_infers_type(values: list[Scalar], expected: ColumnType) -> None:
    assert infer_type(values) == expected


@pytest.mark.parametrize(
    "values",
    [
        [1, "a"],
        [True, 1],
        ["2026-10-01", "soon"],
        ["01/10/2026"],
        ["20261001"],
        ["2026-13-01"],
        ["2026-10-01T14:30:00Z", "2026-10-01T14:30:00"],
    ],
    ids=[
        "number and text",
        "boolean and number",
        "date and text",
        "ambiguous date format",
        "compact date format",
        "invalid month",
        "mixed time zone awareness",
    ],
)
def test_falls_back_to_string(values: list[Scalar]) -> None:
    assert infer_type(values) == ColumnType.STRING


@pytest.mark.parametrize(
    ("value", "column_type", "expected"),
    [
        ("text", ColumnType.STRING, "text"),
        (1, ColumnType.STRING, "1"),
        (True, ColumnType.STRING, "true"),
        (3, ColumnType.NUMBER, 3.0),
        (7, ColumnType.INTEGER, 7),
        (False, ColumnType.BOOLEAN, False),
        ("2026-10-01", ColumnType.DATE, date(2026, 10, 1)),
        (
            "2026-10-01T14:30:00Z",
            ColumnType.DATETIME,
            datetime(2026, 10, 1, 14, 30, tzinfo=UTC),
        ),
        ("2026-10-01", ColumnType.DATETIME, datetime(2026, 10, 1)),
        (None, ColumnType.INTEGER, None),
    ],
)
def test_converts_value(
    value: Scalar, column_type: ColumnType, expected: Value
) -> None:
    converted = convert(value, column_type)

    assert converted == expected
    assert type(converted) is type(expected)
