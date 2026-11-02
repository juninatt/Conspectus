from datetime import date, datetime
from pathlib import Path

import pytest

from conspectus.models import Column, ColumnType
from conspectus.readers import JsonReader, Reader, ReaderError

FIXTURES = Path(__file__).parent.parent / "fixtures"


def write_json(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "data.json"
    path.write_text(content, encoding="utf-8")
    return path


def test_reads_sample_file() -> None:
    reader: Reader = JsonReader(FIXTURES / "measurements.json")

    dataset = reader.read()

    assert dataset.columns == [
        Column(name="timestamp", type=ColumnType.DATETIME, nullable=False),
        Column(name="station", type=ColumnType.STRING, nullable=False),
        Column(name="temperature", type=ColumnType.NUMBER, nullable=True),
        Column(name="samples", type=ColumnType.INTEGER, nullable=False),
        Column(name="active", type=ColumnType.BOOLEAN, nullable=False),
        Column(name="serviced", type=ColumnType.DATE, nullable=True),
    ]
    assert dataset.rows[0] == {
        "timestamp": datetime(2026, 10, 1, 8, 0),
        "station": "north",
        "temperature": 12.5,
        "samples": 42,
        "active": True,
        "serviced": date(2026, 9, 15),
    }
    assert len(dataset.rows) == 3


def test_missing_keys_become_null(tmp_path: Path) -> None:
    path = write_json(tmp_path, '[{"a": 1, "b": 2}, {"a": 3}]')

    dataset = JsonReader(path).read()

    assert dataset.rows[1] == {"a": 3, "b": None}
    assert dataset.columns[1].nullable


def test_orders_columns_by_first_appearance(tmp_path: Path) -> None:
    path = write_json(tmp_path, '[{"b": 1}, {"a": 2, "b": 3}, {"c": 4}]')

    dataset = JsonReader(path).read()

    assert [column.name for column in dataset.columns] == ["b", "a", "c"]


def test_reads_empty_list_as_empty_dataset(tmp_path: Path) -> None:
    dataset = JsonReader(write_json(tmp_path, "[]")).read()

    assert dataset.columns == []
    assert dataset.rows == []


def test_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ReaderError, match="Cannot read"):
        JsonReader(tmp_path / "missing.json").read()


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ('[{"a": 1}', "Invalid JSON"),
        ('{"a": 1}', "expected a list of objects, got dict"),
        ('[{"a": 1}, 2]', "row 2: expected an object, got int"),
        ('[{"a": {"b": 1}}]', "row 1, column 'a': nested values"),
        ('[{"a": [1, 2]}]', "row 1, column 'a': nested values"),
        ('[{"a": NaN}]', "NaN is not valid JSON"),
    ],
    ids=[
        "malformed",
        "not a list",
        "row not an object",
        "nested object",
        "nested list",
        "NaN",
    ],
)
def test_rejects_unsupported_content(
    tmp_path: Path, content: str, message: str
) -> None:
    with pytest.raises(ReaderError, match=message):
        JsonReader(write_json(tmp_path, content)).read()
