"""Creates the right reader for a configured source."""

from typing import assert_never

from conspectus.config import Source
from conspectus.readers.base import Reader
from conspectus.readers.json_reader import JsonReader


def create_reader(source: Source) -> Reader:
    match source.format:
        case "json":
            return JsonReader(source.path, source.columns)
        case _:
            assert_never(source.format)
