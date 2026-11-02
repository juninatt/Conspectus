"""Column type inference for formats without a schema, such as JSON.

Rules:
- Missing values (None) are ignored when inferring; a column of only missing
  values is a string column.
- Only ISO 8601 strings are recognised as dates, so ambiguous formats like
  01/10/2026 stay strings instead of being guessed.
- A column mixing date-only and date-time strings is a datetime column.
- Any other mix of types makes the column a string column.
"""

import json
import re
from collections.abc import Sequence
from datetime import date, datetime

from conspectus.models import ColumnType, Value

type Scalar = str | int | float | bool | None

_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_DATETIME = re.compile(
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d{1,6})?)?(Z|[+-]\d{2}:\d{2})?"
)


def infer_type(values: Sequence[Scalar]) -> ColumnType:
    present = [value for value in values if value is not None]

    if not present:
        return ColumnType.STRING
    if all(isinstance(value, bool) for value in present):
        return ColumnType.BOOLEAN
    if any(isinstance(value, bool) for value in present):
        return ColumnType.STRING
    if all(isinstance(value, int) for value in present):
        return ColumnType.INTEGER
    if all(isinstance(value, int | float) for value in present):
        return ColumnType.NUMBER

    strings = [value for value in present if isinstance(value, str)]
    if len(strings) != len(present):
        return ColumnType.STRING
    if all(_parse_date(value) is not None for value in strings):
        return ColumnType.DATE
    if _is_datetime_column(strings):
        return ColumnType.DATETIME
    return ColumnType.STRING


def convert(value: Scalar, column_type: ColumnType) -> Value:
    """Convert a raw value to the Python type matching its column type."""
    if value is None:
        return None
    match column_type:
        case ColumnType.STRING:
            return value if isinstance(value, str) else json.dumps(value)
        case ColumnType.NUMBER:
            return float(value)
        case ColumnType.DATE if isinstance(value, str):
            return date.fromisoformat(value)
        case ColumnType.DATETIME if isinstance(value, str):
            return datetime.fromisoformat(value)
        case _:
            return value


def _parse_date(value: str) -> date | None:
    if not _DATE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_datetime(value: str) -> datetime | None:
    if not (_DATE.fullmatch(value) or _DATETIME.fullmatch(value)):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _is_datetime_column(values: Sequence[str]) -> bool:
    parsed = [_parse_datetime(value) for value in values]
    if any(moment is None for moment in parsed):
        return False
    # Values with and without a time zone cannot be compared or sorted together.
    aware = {moment.tzinfo is not None for moment in parsed if moment is not None}
    return len(aware) == 1
