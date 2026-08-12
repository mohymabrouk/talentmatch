from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InteractionSnapshot:
    event_type: str
    created_at: datetime
    job_id: str | None = None


@dataclass(frozen=True)
class CandidateSnapshot:
    user_id: str
    current_title: str | None
    target_roles: tuple[str, ...]
    skills: frozenset[str]
    years_experience: float
    location: str | None
    remote_preference: str | None
    interactions: tuple[InteractionSnapshot, ...]


@dataclass(frozen=True)
class JobSnapshot:
    job_id: str
    title: str
    company_name: str
    location: str | None
    remote_mode: str | None
    seniority: str | None
    posted_at: datetime | None
    skills: frozenset[str]
    required_skills: frozenset[str]
    interactions: tuple[InteractionSnapshot, ...]


@dataclass(frozen=True)
class FeatureContext:
    as_of: datetime
    retrieval_score: float = 0.0
    retrieval_position: int = 0

