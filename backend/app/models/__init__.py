"""Persistence entities exposed to application services."""

from app.models.entities import (
    Base,
    CandidateProfile,
    CandidateSkill,
    CandidateTargetRole,
    Interaction,
    Job,
    JobSkill,
    ModelVersion,
    RecommendationItem,
    RecommendationRequest,
    Skill,
    User,
    model_to_dict,
    new_id,
    utcnow,
)

__all__ = [
    "Base",
    "CandidateProfile",
    "CandidateSkill",
    "CandidateTargetRole",
    "Interaction",
    "Job",
    "JobSkill",
    "ModelVersion",
    "RecommendationItem",
    "RecommendationRequest",
    "Skill",
    "User",
    "model_to_dict",
    "new_id",
    "utcnow",
]

