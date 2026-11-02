from pathlib import Path

import pytest

from conspectus.config import Settings


def test_defaults_to_sources_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONSPECTUS_SOURCES", raising=False)

    assert Settings().sources == Path("sources.yaml")


def test_reads_sources_path_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONSPECTUS_SOURCES", "/config/sources.yaml")

    assert Settings().sources == Path("/config/sources.yaml")
