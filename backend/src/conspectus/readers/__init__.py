"""Readers turn a data source into a Dataset, one reader per format."""

from conspectus.readers.base import Reader, ReaderError
from conspectus.readers.json_reader import JsonReader

__all__ = ["JsonReader", "Reader", "ReaderError"]
