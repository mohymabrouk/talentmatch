from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from scripts.seed_jobs import seed


def build_seeded_app(tmp_path: Path):
    settings = Settings(database_url=f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    app = create_app(settings)
    seed(Path(__file__).resolve().parents[2] / "data" / "jobs.jsonl", settings)
    return app


def test_saved_and_application_views_are_persisted_and_scoped(tmp_path: Path) -> None:
    app = build_seeded_app(tmp_path)
    client = TestClient(app)
    profile = client.patch(
        "/api/v1/profile",
        json={"target_roles": ["Machine Learning Engineer"], "skills": ["Python", "PyTorch"]},
    )
    assert profile.status_code == 200
    recommendation = client.get("/api/v1/recommendations?limit=3").json()
    first, second = recommendation["items"][:2]
    request_id = recommendation["recommendation_request_id"]

    save = client.post(
        "/api/v1/interactions",
        json={"job_id": first["job_id"], "event_type": "save", "recommendation_request_id": request_id},
    )
    apply = client.post(
        "/api/v1/interactions",
        json={"job_id": second["job_id"], "event_type": "apply", "recommendation_request_id": request_id},
    )
    assert save.status_code == 201
    assert apply.status_code == 201
    assert client.get("/api/v1/saved-jobs").json()["total"] == 1
    assert client.get("/api/v1/applications").json()["total"] == 1
    assert client.get("/api/v1/saved-jobs?page=2").json()["items"] == []
    assert client.get("/api/v1/saved-jobs", headers={"X-Demo-User-ID": "00000000-0000-0000-0000-000000000099"}).json()["total"] == 0
