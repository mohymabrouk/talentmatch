#!/usr/bin/env python3
import os
import sys

from sqlalchemy import create_engine

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import Settings  # noqa: E402
from app.db.migrations import run_migrations  # noqa: E402


if __name__ == "__main__":
    settings = Settings()
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    )
    run_migrations(engine)
    print(f"Applied migrations for {settings.database_url}")

