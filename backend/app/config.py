from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+pysqlite:///./talentmatch.db"
    demo_user_id: str = "00000000-0000-0000-0000-000000000001"
    demo_user_email: str = "demo@talentmatch.local"
    api_prefix: str = "/api/v1"
    environment: str = "development"
    retrieval_version: str = "retrieval-v001"
    model_version: str = "content-v001"
    retrieval_artifact_dir: str = "ml/artifacts/retrieval/v001"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_recommendation_limit: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

