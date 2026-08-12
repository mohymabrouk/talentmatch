from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ml.features.schema import FEATURE_SCHEMA, FeatureVector


class RankerModel:
    def __init__(self, artifact_dir: Path) -> None:
        metadata = json.loads((artifact_dir / "metadata.json").read_text(encoding="utf-8"))
        schema = json.loads((artifact_dir / "feature_schema.json").read_text(encoding="utf-8"))
        if schema.get("version") != FEATURE_SCHEMA.version:
            raise ValueError("ranker feature schema is incompatible")
        if tuple(item["name"] for item in schema["features"]) != FEATURE_SCHEMA.names:
            raise ValueError("ranker feature order is incompatible")
        if metadata.get("schema_version") != FEATURE_SCHEMA.version:
            raise ValueError("ranker metadata schema is incompatible")
        import lightgbm as lgb

        self.version = str(metadata["version"])
        self.artifact_dir = artifact_dir
        self.booster = lgb.Booster(model_file=str(artifact_dir / "model.txt"))

    def predict(self, vector: FeatureVector) -> float:
        if vector.schema_version != FEATURE_SCHEMA.version or vector.names != FEATURE_SCHEMA.names:
            raise ValueError("feature vector is incompatible with ranker")
        return float(self.booster.predict(np.asarray([vector.values], dtype=np.float32))[0])

