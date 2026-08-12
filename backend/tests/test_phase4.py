from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import Settings
from app.main import create_app
from app.models import ModelVersion, RecommendationRequest
from ml.features.schema import FEATURE_SCHEMA
from ml.ranking.dataset import RankingRow
from ml.ranking.trainer import train_ranker

from scripts.seed_jobs import seed


def build_rows(group_count: int = 9) -> list[RankingRow]:
    rows: list[RankingRow] = []
    start = datetime(2026, 1, 1, tzinfo=UTC)
    for request_number in range(group_count):
        for candidate_number, label in enumerate((1, 0, 0)):
            values = {name: 0.0 for name in FEATURE_SCHEMA.names}
            values["retrieval_score"] = 0.15 if candidate_number == 0 else 0.9 - candidate_number * 0.1
            values["skill_overlap_ratio"] = float(candidate_number == 0)
            values["required_skill_match_ratio"] = float(candidate_number == 0)
            rows.append(
                RankingRow(
                    request_id=f"request-{request_number}",
                    user_id="user-001",
                    job_id=f"job-{request_number}-{candidate_number}",
                    served_at=start + timedelta(days=request_number),
                    label=label,
                    features=FEATURE_SCHEMA.vector(values),
                )
            )
    return rows


def build_seeded_app(tmp_path: Path, ranker_artifact_dir: Path | None = None):
    settings = Settings(
        database_url=f"sqlite+pysqlite:///{tmp_path / 'test.db'}",
        ranker_artifact_dir=str(ranker_artifact_dir or tmp_path / "missing-ranker"),
    )
    app = create_app(settings)
    seed(Path(__file__).resolve().parents[2] / "data" / "jobs.jsonl", settings)
    return app


def configure_profile(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/profile",
        json={"target_roles": ["Machine Learning Engineer"], "skills": ["Python", "PyTorch"]},
    )
    assert response.status_code == 200, response.text


def test_recommendations_fall_back_without_ranker_artifact(tmp_path: Path) -> None:
    app = build_seeded_app(tmp_path)
    client = TestClient(app)
    configure_profile(client)

    response = client.get("/api/v1/recommendations?limit=5")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["model_version"] == "content-v001"

    session = app.state.session_factory()
    try:
        request = session.get(RecommendationRequest, payload["recommendation_request_id"])
        model = session.scalar(select(ModelVersion).where(ModelVersion.version == "content-v001"))
        assert request.fallback_used is True
        assert model.model_type == "content-retrieval"
    finally:
        session.close()


def test_recommendations_use_compatible_ranker_artifact(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "ranker" / "v001"
    train_ranker(build_rows(), artifact_dir, num_boost_round=20)
    app = build_seeded_app(tmp_path, artifact_dir)
    client = TestClient(app)
    configure_profile(client)

    response = client.get("/api/v1/recommendations?limit=5")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["model_version"] == "ranker-v001"
    assert len(payload["items"]) == 5

    session = app.state.session_factory()
    try:
        model = session.scalar(select(ModelVersion).where(ModelVersion.version == "ranker-v001"))
        assert model.model_type == "lightgbm-lambdarank"
        assert model.metrics_json is not None
    finally:
        session.close()
