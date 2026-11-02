"""Reader for tabular JSON: a list of flat objects, one object per row."""

import json
from pathlib import Path
from typing import cast

from conspectus.models import Column, ColumnType, Dataset
from conspectus.readers.base import ReaderError
from conspectus.readers.inference import (
    Scalar,
    TypeMismatch,
    check_type,
    convert,
    infer_type,
)

type Record = dict[str, Scalar]


class JsonReader:
    def __init__(
        self, path: Path, column_types: dict[str, ColumnType] | None = None
    ) -> None:
        """Read `path`; `column_types` overrides the inferred type per column."""
        self._path = path
        self._column_types = column_types or {}

    def read(self) -> Dataset:
        records = self._load()

        # Columns are every key found in any row, in order of first appearance.
        names = list(dict.fromkeys(key for record in records for key in record))
        if records:
            unknown = [name for name in self._column_types if name not in names]
            if unknown:
                raise ReaderError(
                    f"{self._path}: type set for unknown column(s) "
                    + ", ".join(f"'{name}'" for name in unknown)
                )

        columns: list[Column] = []
        values_by_name: dict[str, list[Scalar]] = {}
        for name in names:
            values = [record.get(name) for record in records]
            column_type = self._column_type(name, values)
            columns.append(Column(name=name, type=column_type, nullable=None in values))
            values_by_name[name] = values

        rows = [
            {
                column.name: convert(values_by_name[column.name][index], column.type)
                for column in columns
            }
            for index in range(len(records))
        ]
        return Dataset(columns=columns, rows=rows)

    def _column_type(self, name: str, values: list[Scalar]) -> ColumnType:
        column_type = self._column_types.get(name)
        if column_type is None:
            return infer_type(values)
        try:
            check_type(values, column_type)
        except TypeMismatch as error:
            row = f", row {error.row}" if error.row is not None else ""
            raise ReaderError(
                f"{self._path}{row}, column '{name}': {error.reason}"
            ) from error
        return column_type

    def _load(self) -> list[Record]:
        try:
            text = self._path.read_text(encoding="utf-8")
        except OSError as error:
            raise ReaderError(f"Cannot read {self._path}: {error.strerror}") from error

        try:
            data = json.loads(text, parse_constant=_reject_constant)
        except json.JSONDecodeError as error:
            raise ReaderError(
                f"Invalid JSON in {self._path} at line {error.lineno}, "
                f"column {error.colno}: {error.msg}"
            ) from error

        if not isinstance(data, list):
            raise ReaderError(
                f"{self._path}: expected a list of objects, got {type(data).__name__}"
            )
        for number, record in enumerate(data, start=1):
            if not isinstance(record, dict):
                raise ReaderError(
                    f"{self._path}, row {number}: expected an object, "
                    f"got {type(record).__name__}"
                )
            for key, value in record.items():
                if isinstance(value, dict | list):
                    raise ReaderError(
                        f"{self._path}, row {number}, column '{key}': "
                        "nested values are not supported"
                    )
        return cast(list[Record], data)


def _reject_constant(name: str) -> None:
    raise ReaderError(f"{name} is not valid JSON")
