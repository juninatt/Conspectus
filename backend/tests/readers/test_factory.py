from pathlib import Path

from conspectus.config import load_sources
from conspectus.models import ColumnType
from conspectus.readers import JsonReader, create_reader

BACKEND = Path(__file__).parent.parent.parent


def test_creates_json_reader_with_type_overrides(tmp_path: Path) -> None:
    (tmp_path / "a.json").write_text('[{"n": 1}]', encoding="utf-8")
    config = tmp_path / "sources.yaml"
    config.write_text(
        "sources: [{name: A, format: json, path: a.json, columns: {n: number}}]",
        encoding="utf-8",
    )
    [source] = load_sources(config)

    reader = create_reader(source)

    assert isinstance(reader, JsonReader)
    assert reader.read().columns[0].type == ColumnType.NUMBER


def test_example_configuration_is_valid_and_readable() -> None:
    sources = load_sources(BACKEND / "sources.example.yaml")

    for source in sources:
        assert create_reader(source).read().rows
