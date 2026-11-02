from datetime import date

import pytest
from pydantic import ValidationError

from conspectus.models import Column, ColumnType, Dataset, Value


def test_accepts_rows_matching_columns() -> None:
    dataset = Dataset(
        columns=[Column(name="day", type=ColumnType.DATE, nullable=False)],
        rows=[{"day": date(2026, 10, 1)}],
    )

    assert dataset.rows[0]["day"] == date(2026, 10, 1)


def test_rejects_duplicate_column_names() -> None:
    column = Column(name="day", type=ColumnType.DATE, nullable=False)

    with pytest.raises(ValidationError, match="unique"):
        Dataset(columns=[column, column], rows=[])


@pytest.mark.parametrize(
    "row",
    [{}, {"day": None, "extra": 1}],
    ids=["missing column", "unknown column"],
)
def test_rejects_row_not_matching_columns(row: dict[str, Value]) -> None:
    with pytest.raises(ValidationError, match="row 1"):
        Dataset(
            columns=[Column(name="day", type=ColumnType.DATE, nullable=True)],
            rows=[row],
        )


def test_serializes_dates_as_iso_strings() -> None:
    dataset = Dataset(
        columns=[Column(name="day", type=ColumnType.DATE, nullable=False)],
        rows=[{"day": date(2026, 10, 1)}],
    )

    assert dataset.model_dump(mode="json")["rows"] == [{"day": "2026-10-01"}]
