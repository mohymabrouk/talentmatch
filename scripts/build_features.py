#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import Settings  # noqa: E402
from app.db.session import build_session_factory  # noqa: E402
from ml.features.dataset import FeatureDatasetBuilder  # noqa: E402
from ml.features.schema import FEATURE_SCHEMA  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Build point-in-time recommendation features.")
    parser.add_argument("--output", type=Path, default=Path("ml/artifacts/features/v001/training.jsonl"))
    args = parser.parse_args()
    settings = Settings()
    _, factory = build_session_factory(settings)
    db = factory()
    try:
        rows = FeatureDatasetBuilder(db).build()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row.to_record(), sort_keys=True) + "\n")
        print(f"wrote {len(rows)} rows using {FEATURE_SCHEMA.version} to {args.output}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

