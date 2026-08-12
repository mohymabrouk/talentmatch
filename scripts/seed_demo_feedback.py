#!/usr/bin/env python3
"""Create deterministic recommendation impressions and positive feedback for local training."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import select  # noqa: E402

from app.api.routes.profile import ensure_user  # noqa: E402
from app.core.config import Settings  # noqa: E402
from app.db.session import build_session_factory  # noqa: E402
from app.models import (  # noqa: E402
    CandidateProfile,
    CandidateSkill,
    CandidateTargetRole,
    Interaction,
    Job,
    ModelVersion,
    RecommendationItem,
    RecommendationRequest,
    Skill,
)


DEMO_REQUEST_COUNT = 12
POSITIVE_EXTERNAL_IDS = ("demo-001", "demo-002", "demo-007", "demo-009", "demo-012")
NEGATIVE_EXTERNAL_IDS = ("demo-003", "demo-006", "demo-008", "demo-010", "demo-011")


def ensure_profile(db, user_id: str) -> None:
    ensure_user(db, user_id)
    profile = db.get(CandidateProfile, user_id)
    if profile is None:
        profile = CandidateProfile(
            user_id=user_id,
            current_title="Machine Learning Engineer",
            years_experience=4.0,
            location="Paris, France",
            remote_preference="any",
        )
        db.add(profile)

    existing_roles = set(
        db.scalars(select(CandidateTargetRole.role_name).where(CandidateTargetRole.user_id == user_id)).all()
    )
    for priority, role_name in enumerate(("Machine Learning Engineer", "Applied AI Engineer")):
        if role_name not in existing_roles:
            db.add(CandidateTargetRole(user_id=user_id, role_name=role_name, priority=priority))

    existing_skill_ids = {
        skill_id for skill_id, in db.execute(select(CandidateSkill.skill_id).where(CandidateSkill.user_id == user_id))
    }
    for display_name in ("Python", "PyTorch", "SQL", "FAISS"):
        normalized = display_name.casefold()
        skill = db.scalar(select(Skill).where(Skill.normalized == normalized))
        if skill is None:
            skill = Skill(normalized=normalized, display_name=display_name)
            db.add(skill)
            db.flush()
        if skill.id not in existing_skill_ids:
            db.add(CandidateSkill(user_id=user_id, skill_id=skill.id, proficiency=4))
            existing_skill_ids.add(skill.id)


def seed(settings: Settings) -> int:
    _, factory = build_session_factory(settings)
    db = factory()
    try:
        ensure_profile(db, settings.demo_user_id)
        jobs = {
            job.external_id: job
            for job in db.scalars(
                select(Job).where(Job.external_id.in_(POSITIVE_EXTERNAL_IDS + NEGATIVE_EXTERNAL_IDS))
            ).all()
        }
        expected = set(POSITIVE_EXTERNAL_IDS + NEGATIVE_EXTERNAL_IDS)
        missing = sorted(expected - set(jobs))
        if missing:
            raise RuntimeError(f"seed jobs first; missing external IDs: {', '.join(missing)}")

        created = 0
        start = datetime(2026, 8, 1, 12, 0, 0)
        for request_number in range(DEMO_REQUEST_COUNT):
            request_id = str(uuid5(NAMESPACE_URL, f"talentmatch-demo-feedback:{request_number}"))
            if db.get(RecommendationRequest, request_id) is not None:
                continue
            served_at = start + timedelta(days=request_number)
            positive_external_id = POSITIVE_EXTERNAL_IDS[request_number % len(POSITIVE_EXTERNAL_IDS)]
            negative_external_id = NEGATIVE_EXTERNAL_IDS[request_number % len(NEGATIVE_EXTERNAL_IDS)]
            candidate_external_ids = [
                negative_external_id,
                NEGATIVE_EXTERNAL_IDS[(request_number + 1) % len(NEGATIVE_EXTERNAL_IDS)],
                positive_external_id,
            ]
            if len(set(candidate_external_ids)) != 3:
                raise RuntimeError(f"duplicate demo candidates for request {request_id}")

            request = RecommendationRequest(
                id=request_id,
                user_id=settings.demo_user_id,
                model_version=settings.model_version,
                retrieval_version=settings.retrieval_version,
                candidate_count=3,
                returned_count=3,
                latency_ms=1,
                fallback_used=True,
                created_at=served_at,
            )
            db.add(request)
            for position, external_id in enumerate(candidate_external_ids, start=1):
                job = jobs[external_id]
                retrieval_score = 0.95 - (position - 1) * 0.1
                if external_id == positive_external_id:
                    retrieval_score = 0.15
                db.add(
                    RecommendationItem(
                        request_id=request_id,
                        job_id=job.id,
                        position=position,
                        retrieval_score=retrieval_score,
                        ranking_score=retrieval_score,
                    )
                )
                db.add(
                    Interaction(
                        user_id=settings.demo_user_id,
                        job_id=job.id,
                        event_type="impression",
                        recommendation_request_id=request_id,
                        model_version=settings.model_version,
                        created_at=served_at + timedelta(seconds=position),
                    )
                )
            positive_job = jobs[positive_external_id]
            db.add(
                Interaction(
                    user_id=settings.demo_user_id,
                    job_id=positive_job.id,
                    event_type="apply" if request_number % 3 == 0 else "save",
                    recommendation_request_id=request_id,
                    model_version=settings.model_version,
                    created_at=served_at + timedelta(hours=6),
                )
            )
            created += 1
        db.commit()
        return created
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    settings = Settings()
    print(f"Created {seed(settings)} deterministic recommendation requests")
