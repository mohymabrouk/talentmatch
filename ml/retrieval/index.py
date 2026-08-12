from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ml.retrieval.embeddings import build_embedder
from ml.retrieval.text import job_text


@dataclass(frozen=True)
class SearchResult:
    item_id: str
    score: float
    position: int


class VectorIndex:
    def __init__(self, item_ids: list[str], embeddings: np.ndarray, backend: str = "numpy") -> None:
        self.item_ids = item_ids
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.backend = backend
        self._faiss_index = None
        if backend == "faiss":
            import faiss

            self._faiss_index = faiss.IndexFlatIP(self.embeddings.shape[1])
            self._faiss_index.add(self.embeddings)

    @classmethod
    def build(cls, item_ids: list[str], embeddings: np.ndarray, prefer_faiss: bool = True) -> "VectorIndex":
        normalized = np.asarray(embeddings, dtype=np.float32)
        norms = np.linalg.norm(normalized, axis=1, keepdims=True)
        normalized = normalized / np.maximum(norms, 1e-12)
        if prefer_faiss:
            try:
                import faiss  # noqa: F401

                return cls(item_ids, normalized, backend="faiss")
            except Exception:
                pass
        return cls(item_ids, normalized, backend="numpy")

    def search(self, query: np.ndarray, k: int) -> list[SearchResult]:
        if not self.item_ids:
            return []
        vector = np.asarray(query, dtype=np.float32).reshape(1, -1)
        vector /= max(float(np.linalg.norm(vector)), 1e-12)
        limit = min(max(k, 1), len(self.item_ids))
        if self._faiss_index is not None:
            scores, positions = self._faiss_index.search(vector, limit)
            return [
                SearchResult(self.item_ids[int(position)], float(score), int(position))
                for score, position in zip(scores[0], positions[0])
                if position >= 0
            ]
        scores = self.embeddings @ vector[0]
        positions = np.argsort(-scores)[:limit]
        return [
            SearchResult(self.item_ids[int(position)], float(scores[position]), int(position))
            for position in positions
        ]

    def save(self, directory: Path, metadata: dict[str, object] | None = None) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        np.save(directory / "embeddings.npy", self.embeddings)
        np.save(directory / "item_ids.npy", np.asarray(self.item_ids))
        artifact_metadata = {
            "backend": self.backend,
            "dimension": int(self.embeddings.shape[1]),
            "count": len(self.item_ids),
            **(metadata or {}),
        }
        (directory / "metadata.json").write_text(json.dumps(artifact_metadata, indent=2, sort_keys=True) + "\n")
        if self.backend == "faiss" and self._faiss_index is not None:
            import faiss

            faiss.write_index(self._faiss_index, str(directory / "faiss.index"))

    @classmethod
    def load(cls, directory: Path) -> "VectorIndex":
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        embeddings = np.load(directory / "embeddings.npy")
        item_ids = [str(value) for value in np.load(directory / "item_ids.npy", allow_pickle=False).tolist()]
        backend = str(metadata.get("backend", "numpy"))
        index = cls(item_ids, embeddings, backend="numpy")
        if backend == "faiss" and (directory / "faiss.index").exists():
            try:
                import faiss

                index.backend = "faiss"
                index._faiss_index = faiss.read_index(str(directory / "faiss.index"))
            except Exception:
                pass
        return index


def build_job_index(db, settings, output_dir: Path, prefer_sentence_transformer: bool = True) -> dict[str, object]:
    from sqlalchemy import select

    from app.models import Job, JobSkill, Skill

    jobs = db.scalars(select(Job).where(Job.is_active.is_(True)).order_by(Job.id)).all()
    skill_rows = db.execute(
        select(JobSkill.job_id, Skill.display_name)
        .join(Skill, Skill.id == JobSkill.skill_id)
        .where(JobSkill.job_id.in_([job.id for job in jobs]))
    ).all() if jobs else []
    skills_by_job: dict[str, list[str]] = {}
    for job_id, display_name in skill_rows:
        skills_by_job.setdefault(job_id, []).append(display_name)
    embedder = build_embedder(settings.embedding_model, prefer_sentence_transformer=prefer_sentence_transformer)
    embeddings = embedder.encode([job_text(job, skills_by_job.get(job.id, [])) for job in jobs])
    index = VectorIndex.build([job.id for job in jobs], embeddings)
    index.save(
        output_dir,
        metadata={"embedding_model": embedder.name, "retrieval_version": settings.retrieval_version},
    )
    return {"count": len(jobs), "dimension": int(embeddings.shape[1]), "backend": index.backend, "model": embedder.name}
