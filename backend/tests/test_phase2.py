from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.config import Settings
from app.models import Interaction, RecommendationItem
from app.main import create_app

from scripts.seed_jobs import seed


def build_seeded_app(tmp_path: Path):
    settings = Settings(database_url=f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    app = create_app(settings)
    seed(Path(__file__).resolve().parents[2] / "data" / "jobs.jsonl", settings)
    return app


def test_impressions_and_behavioral_events_are_linked_to_served_items(tmp_path: Path):
    app = build_seeded_app(tmp_path)
    client = TestClient(app)
    client.patch("/api/v1/profile", json={"target_roles": ["Machine Learning Engineer"], "skills": ["Python", "PyTorch"]})
    recommendation = client.get("/api/v1/recommendations?limit=5").json()
    request_id = recommendation["recommendation_request_id"]
    items = recommendation["items"]
    assert [item["position"] for item in items] == list(range(1, len(items) + 1))

    session = app.state.session_factory()
    try:
        impressions = session.scalar(
            select(func.count()).select_from(Interaction).where(
                Interaction.recommendation_request_id == request_id,
                Interaction.event_type == "impression",
            )
        )
        assert impressions == len(items)
    finally:
        session.close()

    event = client.post(
        "/api/v1/interactions",
        json={"job_id": items[0]["job_id"], "event_type": "save", "recommendation_request_id": request_id},
    )
    assert event.status_code == 201
    assert event.json()["model_version"] == recommendation["model_version"]

    unserved_job = client.get("/api/v1/jobs").json()["items"][-1]["id"]
    if unserved_job not in {item["job_id"] for item in items}:
        rejected = client.post(
            "/api/v1/interactions",
            json={"job_id": unserved_job, "event_type": "click", "recommendation_request_id": request_id},
        )
        assert rejected.status_code == 400


def test_unknown_request_is_rejected(tmp_path: Path):
    app = build_seeded_app(tmp_path)
    client = TestClient(app)
    job_id = client.get("/api/v1/jobs").json()["items"][0]["id"]
    response = client.post(
        "/api/v1/interactions",
        json={"job_id": job_id, "event_type": "click", "recommendation_request_id": "00000000-0000-0000-0000-000000000099"},
    )
    assert response.status_code == 404
