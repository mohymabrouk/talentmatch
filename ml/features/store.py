from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    CandidateProfile,
    CandidateSkill,
    CandidateTargetRole,
    Interaction,
    Job,
    JobSkill,
    Skill,
)
from ml.features.builder import FeatureBuilder
from ml.features.schema import FEATURE_SCHEMA, FeatureSchema, FeatureVector
from ml.features.types import CandidateSnapshot, FeatureContext, InteractionSnapshot, JobSnapshot


class FeatureStore:
    """Loads point-in-time snapshots and delegates every value to FeatureBuilder."""

    def __init__(self, db: Session, as_of: datetime, schema: FeatureSchema = FEATURE_SCHEMA) -> None:
        self.db = db
        self.as_of = as_of
        self.builder = FeatureBuilder(schema)
        self._candidate_cache: dict[str, CandidateSnapshot] = {}
        self._job_cache: dict[str, JobSnapshot] = {}

    def candidate(self, user_id: str) -> CandidateSnapshot:
        if user_id in self._candidate_cache:
            return self._candidate_cache[user_id]
        profile = self.db.get(CandidateProfile, user_id)
        roles = tuple(
            self.db.scalars(
                select(CandidateTargetRole.role_name)
                .where(CandidateTargetRole.user_id == user_id)
                .order_by(CandidateTargetRole.priority, CandidateTargetRole.role_name)
            ).all()
        )
        skills = frozenset(
            self.db.scalars(
                select(Skill.normalized)
                .join(CandidateSkill, CandidateSkill.skill_id == Skill.id)
                .where(CandidateSkill.user_id == user_id)
            ).all()
        )
        interactions = tuple(
            InteractionSnapshot(event.event_type, event.created_at, event.job_id)
            for event in self.db.scalars(
                select(Interaction)
                .where(Interaction.user_id == user_id, Interaction.created_at <= self.as_of)
                .order_by(Interaction.created_at, Interaction.id)
            ).all()
        )
        snapshot = CandidateSnapshot(
            user_id=user_id,
            current_title=profile.current_title if profile else None,
            target_roles=roles,
            skills=skills,
            years_experience=float(profile.years_experience or 0.0) if profile else 0.0,
            location=profile.location if profile else None,
            remote_preference=profile.remote_preference if profile else None,
            interactions=interactions,
        )
        self._candidate_cache[user_id] = snapshot
        return snapshot

    def job(self, job_id: str) -> JobSnapshot:
        if job_id in self._job_cache:
            return self._job_cache[job_id]
        job = self.db.get(Job, job_id)
        if job is None:
            raise ValueError(f"job not found: {job_id}")
        skill_rows = self.db.execute(
            select(Skill.normalized, JobSkill.required)
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .where(JobSkill.job_id == job_id)
        ).all()
        skills = frozenset(normalized for normalized, _ in skill_rows)
        required_skills = frozenset(normalized for normalized, required in skill_rows if required)
        interactions = tuple(
            InteractionSnapshot(event.event_type, event.created_at, event.job_id)
            for event in self.db.scalars(
                select(Interaction)
                .where(Interaction.job_id == job_id, Interaction.created_at <= self.as_of)
                .order_by(Interaction.created_at, Interaction.id)
            ).all()
        )
        snapshot = JobSnapshot(
            job_id=job.id,
            title=job.title,
            company_name=job.company_name,
            location=job.location,
            remote_mode=job.remote_mode,
            seniority=job.seniority,
            posted_at=job.posted_at,
            skills=skills,
            required_skills=required_skills,
            interactions=interactions,
        )
        self._job_cache[job_id] = snapshot
        return snapshot

    def build(
        self,
        user_id: str,
        job_id: str,
        retrieval_score: float = 0.0,
        retrieval_position: int = 0,
    ) -> FeatureVector:
        return self.builder.build_vector(
            self.candidate(user_id),
            self.job(job_id),
            FeatureContext(
                as_of=self.as_of,
                retrieval_score=retrieval_score,
                retrieval_position=retrieval_position,
            ),
        )

