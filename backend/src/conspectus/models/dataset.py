"""The common dataset model that every reader produces."""

from datetime import date, datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

type Value = str | int | float | bool | date | datetime | None


class ColumnType(StrEnum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"


class Column(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    type: ColumnType
    nullable: bool


class Dataset(BaseModel):
    """Tabular data: typed columns and rows keyed by column name."""

    model_config = ConfigDict(frozen=True)

    columns: list[Column]
    rows: list[dict[str, Value]]

    @model_validator(mode="after")
    def _check_rows_match_columns(self) -> Self:
        names = [column.name for column in self.columns]
        if len(set(names)) != len(names):
            raise ValueError("column names must be unique")

        expected = set(names)
        for number, row in enumerate(self.rows, start=1):
            if row.keys() != expected:
                raise ValueError(f"row {number} does not match the columns")
        return self
