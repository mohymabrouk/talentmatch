from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def build_test_app(tmp_path: Path):
    return create_app(
        Settings(
            database_url=f"sqlite+pysqlite:///{tmp_path / 'test.db'}",
            demo_user_id="00000000-0000-0000-0000-000000000001",
        )
    )


def test_health_readiness_and_profile_round_trip(tmp_path: Path):
    client = TestClient(build_test_app(tmp_path))
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert client.get("/api/v1/ready").json()["status"] == "ready"

    profile = client.patch(
        "/api/v1/profile",
        json={
            "target_roles": ["Machine Learning Engineer"],
            "skills": ["Python", "PyTorch"],
            "years_experience": 3,
            "remote_preference": "hybrid",
        },
    )
    assert profile.status_code == 200
    assert profile.json()["skills"] == ["PyTorch", "Python"]
    assert client.get("/api/v1/profile").json()["target_roles"] == ["Machine Learning Engineer"]


def test_jobs_filters_and_404(tmp_path: Path):
    client = TestClient(build_test_app(tmp_path))
    assert client.get("/api/v1/jobs").status_code == 200
    assert client.get("/api/v1/jobs/missing").status_code == 404
    assert client.get("/api/v1/profile", headers={"X-Demo-User-ID": "not-a-uuid"}).status_code == 400
    cors = client.options(
        "/api/v1/jobs",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )
    assert cors.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "POST" in cors.headers["access-control-allow-methods"]
