#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import Settings  # noqa: E402
from app.db.session import build_session_factory  # noqa: E402
from ml.retrieval.index import build_job_index  # noqa: E402


if __name__ == "__main__":
    settings = Settings()
    _, factory = build_session_factory(settings)
    db = factory()
    try:
        result = build_job_index(db, settings, Path(settings.retrieval_artifact_dir))
        print(result)
    finally:
        db.close()
