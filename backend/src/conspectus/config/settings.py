"""Application settings, read from CONSPECTUS_* environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CONSPECTUS_")

    # Source configuration file; a relative path is resolved from the
    # directory the application is started in.
    sources: Path = Path("sources.yaml")
