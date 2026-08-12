from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CandidateProfile, CandidateSkill, CandidateTargetRole, Job, JobSkill, Skill
from ml.features.store import FeatureStore
from ml.retrieval.embeddings import build_embedder
from ml.retrieval.index import VectorIndex
from ml.retrieval.text import candidate_text, job_text


@dataclass(frozen=True)
class ScoredJob:
    job: Job
    score: float
    retrieval_score: float
    reasons: list[str]


class RecommendationService:
    def __init__(self, db: Session, settings) -> None:
        self.db = db
        self.settings = settings
        self.jobs = db.scalars(select(Job).where(Job.is_active.is_(True))).all()
        self.jobs_by_id = {job.id: job for job in self.jobs}
        self.skills_by_job: dict[str, set[str]] = {}
        for job_id, normalized in db.execute(
            select(JobSkill.job_id, Skill.normalized)
            .join(Skill, Skill.id == JobSkill.skill_id)
            .where(JobSkill.job_id.in_(list(self.jobs_by_id)))
        ).all():
            self.skills_by_job.setdefault(job_id, set()).add(normalized)
        self.embedder = build_embedder(settings.embedding_model)
        artifact_dir = Path(settings.retrieval_artifact_dir)
        self.fallback_used = True
        if (artifact_dir / "metadata.json").exists():
            try:
                loaded_index = VectorIndex.load(artifact_dir)
                if loaded_index.embeddings.shape[1] != self.embedder.dimension:
                    raise ValueError(
                        "retrieval artifact dimension does not match the active embedding backend"
                    )
                self.index = loaded_index
                self.fallback_used = False
            except Exception:
                self.index = self._build_fallback_index()
        else:
            self.index = self._build_fallback_index()

    def _build_fallback_index(self) -> VectorIndex:
        texts = [job_text(job, self.skills_by_job.get(job.id, set())) for job in self.jobs]
        embeddings = self.embedder.encode(texts)
        return VectorIndex.build([job.id for job in self.jobs], embeddings)

    def recommend(self, user_id: str, limit: int) -> tuple[list[ScoredJob], int]:
        profile = self.db.get(CandidateProfile, user_id)
        roles = list(
            self.db.scalars(
                select(CandidateTargetRole.role_name)
                .where(CandidateTargetRole.user_id == user_id)
                .order_by(CandidateTargetRole.priority)
            ).all()
        )
        skills = list(
            self.db.scalars(
                select(Skill.normalized)
                .join(CandidateSkill, CandidateSkill.skill_id == Skill.id)
                .where(CandidateSkill.user_id == user_id)
            ).all()
        )
        if not roles and not skills:
            raise ValueError("Add at least one target role or skill before requesting recommendations.")
        profile_text = candidate_text(
            roles,
            skills,
            profile.years_experience if profile else None,
            profile.location if profile else None,
            profile.remote_preference if profile else None,
        )
        query = self.embedder.encode([profile_text])[0]
        retrieval = self.index.search(query, min(200, len(self.jobs)))
        candidate_count = len(retrieval)
        feature_store = FeatureStore(self.db, datetime.now(UTC).replace(tzinfo=None))
        scored: list[ScoredJob] = []
        for retrieval_position, result in enumerate(retrieval, start=1):
            job = self.jobs_by_id.get(result.item_id)
            if job is None:
                continue
            feature_values = feature_store.build(
                user_id,
                job.id,
                retrieval_score=result.score,
                retrieval_position=retrieval_position,
            ).as_dict()
            skill_ratio = feature_values["skill_overlap_ratio"]
            role_match = feature_values["candidate_job_title_overlap"]
            compatibility = feature_values["remote_compatible"]
            similarity = max(0.0, min(1.0, (feature_values["retrieval_score"] + 1.0) / 2.0))
            score = max(0.0, min(1.0, 0.65 * similarity + 0.2 * skill_ratio + 0.1 * role_match + 0.05 * compatibility))
            reasons = self._reasons(skill_ratio, role_match, compatibility, similarity)
            scored.append(ScoredJob(job, score, float(result.score), reasons))
        scored.sort(
            key=lambda item: (
                -item.score,
                -(item.job.posted_at or item.job.created_at).timestamp(),
            )
        )
        return scored[:limit], candidate_count

    @staticmethod
    def _role_match(role: str, title: str) -> float:
        role_tokens = set(role.casefold().split())
        title_tokens = set(title.casefold().split())
        if role.casefold() in title.casefold():
            return 1.0
        return len(role_tokens & title_tokens) / len(role_tokens) if role_tokens else 0.0

    @staticmethod
    def _compatibility(profile: CandidateProfile | None, job: Job) -> float:
        if profile is None or not profile.remote_preference or profile.remote_preference == "any":
            return 1.0
        if profile.remote_preference == job.remote_mode:
            return 1.0
        return 0.0

    @staticmethod
    def _reasons(skill_ratio: float, role_match: float, compatibility: float, similarity: float) -> list[str]:
        reasons: list[str] = []
        if skill_ratio >= 0.5:
            reasons.append("Strong skill overlap")
        elif skill_ratio > 0:
            reasons.append("Some matching skills")
        if role_match >= 0.75:
            reasons.append("Matches preferred role")
        if compatibility == 1.0:
            reasons.append("Matches work preference")
        if similarity >= 0.65 or not reasons:
            reasons.append("Similar job content")
        return reasons[:3]
