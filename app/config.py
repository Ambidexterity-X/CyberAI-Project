from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    data_dir: Path = Field(default=Path("data"), alias="DATA_DIR")
    shared_dir: Path = Field(default=Path("data/shared"), alias="SHARED_DIR")
    match_threshold: float = Field(default=0.6, alias="MATCH_THRESHOLD")
    api_title: str = "CyberAI Face Search API"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def registry_path(self) -> Path:
        return self.data_dir / "registry.json"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.shared_dir.mkdir(parents=True, exist_ok=True)
    return settings
