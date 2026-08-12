import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.config import Settings
from app.db.models import RecommendationItem, RecommendationRequest
from app.main import create_app
from ml.evaluation.metrics import mrr, ndcg_at_k, recall_at_k
from ml.retrieval.embeddings import HashingEmbedder
from ml.retrieval.index import VectorIndex
from ml.retrieval.text import job_text

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from seed_jobs import seed  # noqa: E402


def build_seeded_app(tmp_path: Path):
    settings = Settings(database_url=f"sqlite+pysqlite:///{tmp_path / 'test.db'}")
    app = create_app(settings)
    seed(Path(__file__).resolve().parents[2] / "data" / "jobs.jsonl", settings)
    return app


def test_index_round_trip_and_metrics(tmp_path: Path):
    embedder = HashingEmbedder(dimension=32)
    index = VectorIndex.build(["python", "frontend", "data"], embedder.encode(["python pytorch", "typescript react", "sql statistics"]))
    index.save(tmp_path, {"test": True})
    loaded = VectorIndex.load(tmp_path)
    results = loaded.search(embedder.encode(["python"])[0], 2)
    assert results[0].item_id == "python"
    assert results[1].item_id in {"frontend", "data"}
    assert recall_at_k(["a", "b"], ["b"], 2) == 1.0
    assert ndcg_at_k(["b", "a"], ["b"], 2) == 1.0
    assert mrr(["a", "b"], ["b"]) == 0.5


def test_job_text_is_stable_for_unordered_skills():
    class JobFixture:
        title = "Python Engineer"
        company_name = "Acme"
        location = "Paris"
        remote_mode = "hybrid"
        seniority = "mid"
        description = "Build services"

    assert job_text(JobFixture(), {"SQL", "Python"}) == job_text(JobFixture(), {"Python", "SQL"})


def test_recommendations_persist_request_and_positions(tmp_path: Path):
    app = build_seeded_app(tmp_path)
    client = TestClient(app)
    profile = client.patch(
        "/api/v1/profile",
        json={"target_roles": ["Machine Learning Engineer"], "skills": ["Python", "PyTorch"], "remote_preference": "hybrid"},
    )
    assert profile.status_code == 200
    response = client.get("/api/v1/recommendations?limit=20")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["recommendation_request_id"]
    assert 1 <= len(data["items"]) <= 20
    assert data["items"][0]["match_reasons"]
    session = app.state.session_factory()
    try:
        request = session.get(RecommendationRequest, data["recommendation_request_id"])
        items = session.scalars(select(RecommendationItem).where(RecommendationItem.request_id == request.id).order_by(RecommendationItem.position)).all()
        assert request.returned_count == len(data["items"])
        assert [item.position for item in items] == list(range(1, len(items) + 1))
    finally:
        session.close()
