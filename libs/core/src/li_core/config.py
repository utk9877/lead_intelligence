"""Environment-driven settings (pydantic-settings); no config files in prod."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # "dev" | "production". In production the app refuses to start on insecure
    # defaults (see li_api) — it fails closed, never open.
    environment: str = "dev"
    database_url: str = "postgresql+psycopg://li:li_dev_password@localhost:5432/lead_intelligence"
    evidence_bucket: str = "evidence-snapshots"
    # Internal API auth (QA console → api). Dev default; real value comes from env.
    internal_api_key: str = "dev-internal-key"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


# The insecure dev default — production must override it (checked at app startup).
DEV_INTERNAL_API_KEY = "dev-internal-key"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
