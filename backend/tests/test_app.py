from importlib.metadata import version

from conspectus.main import create_app


def test_app_version_matches_package_version() -> None:
    assert create_app().version == version("conspectus")
