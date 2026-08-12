#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select  # noqa: E402

from app.config import Settings  # noqa: E402
from app.db.models import Job, JobSkill, Skill  # noqa: E402
from app.db.session import build_session_factory  # noqa: E402
from ml.evaluation.metrics import mrr, ndcg_at_k, recall_at_k  # noqa: E402
from ml.retrieval.embeddings import build_embedder  # noqa: E402
from ml.retrieval.index import VectorIndex  # noqa: E402
from ml.retrieval.text import candidate_text  # noqa: E402


if __name__ == "__main__":
    settings = Settings()
    _, factory = build_session_factory(settings)
    db = factory()
    try:
        artifact_dir = Path(settings.retrieval_artifact_dir)
        index = VectorIndex.load(artifact_dir) if (artifact_dir / "metadata.json").exists() else None
        jobs = db.scalars(select(Job).where(Job.is_active.is_(True))).all()
        if index is None:
            from ml.retrieval.index import build_job_index

            build_job_index(db, settings, artifact_dir)
            index = VectorIndex.load(artifact_dir)
        by_external = {job.external_id: job.id for job in jobs}
        embedder = build_embedder(settings.embedding_model)
        records = [json.loads(line) for line in Path("data/evaluation.jsonl").read_text().splitlines() if line.strip()]
        metrics = {"recall@20": [], "ndcg@20": [], "mrr": []}
        for record in records:
            vector = embedder.encode([candidate_text(record["target_roles"], record["skills"], record["years_experience"], record["location"], record["remote_preference"])])[0]
            recommended = [item.item_id for item in index.search(vector, 20)]
            relevant = [by_external[item] for item in record["relevant_external_ids"]]
            metrics["recall@20"].append(recall_at_k(recommended, relevant, 20))
            metrics["ndcg@20"].append(ndcg_at_k(recommended, relevant, 20))
            metrics["mrr"].append(mrr(recommended, relevant))
        result = {name: round(sum(values) / len(values), 6) for name, values in metrics.items()}
        print(json.dumps({"cases": len(records), **result}, indent=2))
    finally:
        db.close()

