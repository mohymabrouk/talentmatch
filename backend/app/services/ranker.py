from __future__ import annotations

from pathlib import Path

from ml.features.schema import FeatureVector
from ml.ranking.model import RankerModel


class RankerProvider:
    """Loads a compatible ranker artifact and degrades to content scoring on failure."""

    def __init__(self, settings) -> None:
        self._settings = settings
        self.model: RankerModel | None = None
        self.model_version = settings.model_version
        self.model_type = "content-retrieval"
        self.artifact_path = settings.retrieval_artifact_dir
        self.metrics_json: str | None = None
        self.fallback_used = True

        artifact_dir = Path(settings.ranker_artifact_dir)
        required_files = ("model.txt", "metadata.json", "feature_schema.json")
        if not all((artifact_dir / filename).is_file() for filename in required_files):
            return
        try:
            model = RankerModel(artifact_dir)
            metrics_path = artifact_dir / "metrics.json"
            metrics_json = metrics_path.read_text(encoding="utf-8") if metrics_path.is_file() else None
        except (OSError, ImportError, KeyError, TypeError, ValueError):
            return

        self.model = model
        self.model_version = model.version
        self.model_type = "lightgbm-lambdarank"
        self.artifact_path = str(artifact_dir)
        self.metrics_json = metrics_json
        self.fallback_used = False

    @property
    def available(self) -> bool:
        return self.model is not None

    def predict(self, vector: FeatureVector) -> float | None:
        if self.model is None:
            return None
        try:
            return self.model.predict(vector)
        except (OSError, ValueError, TypeError, RuntimeError):
            self.model = None
            self.model_version = self._settings.model_version
            self.model_type = "content-retrieval"
            self.artifact_path = self._settings.retrieval_artifact_dir
            self.metrics_json = None
            self.fallback_used = True
            return None
