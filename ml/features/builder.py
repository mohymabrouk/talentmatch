from __future__ import annotations

from datetime import timedelta
from re import findall

from ml.features.schema import FEATURE_SCHEMA, FeatureSchema, FeatureVector
from ml.features.types import CandidateSnapshot, FeatureContext, JobSnapshot


def _tokens(value: str | None) -> set[str]:
    return set(findall(r"[a-z0-9][a-z0-9+#.-]*", (value or "").casefold()))


def _events_in_window(events, as_of, days: int):
    start = as_of - timedelta(days=days)
    return tuple(event for event in events if start <= event.created_at <= as_of)


def _event_count(events, event_type: str) -> int:
    return sum(event.event_type == event_type for event in events)


class FeatureBuilder:
    """Canonical feature calculation used for both request-time and training rows."""

    def __init__(self, schema: FeatureSchema = FEATURE_SCHEMA) -> None:
        self.schema = schema

    def build(self, candidate: CandidateSnapshot, job: JobSnapshot, context: FeatureContext) -> dict[str, float]:
        user_events_7d = _events_in_window(candidate.interactions, context.as_of, 7)
        user_events_30d = _events_in_window(candidate.interactions, context.as_of, 30)
        job_events_30d = _events_in_window(job.interactions, context.as_of, 30)
        event_denominator = max(len(user_events_30d), 1)

        overlap = candidate.skills & job.skills
        required_overlap = candidate.skills & job.required_skills
        role_overlap = max((self._role_title_overlap(role, job.title) for role in candidate.target_roles), default=0.0)
        exact_role = float(any(role.casefold() in job.title.casefold() for role in candidate.target_roles))
        job_age_days = 0.0
        if job.posted_at is not None:
            job_age_days = max(0.0, (context.as_of - job.posted_at).total_seconds() / 86400.0)

        values = {
            "user_years_experience": max(0.0, candidate.years_experience),
            "user_skill_count": float(len(candidate.skills)),
            "user_target_role_count": float(len(candidate.target_roles)),
            "user_interaction_count_7d": float(len(user_events_7d)),
            "user_interaction_count_30d": float(len(user_events_30d)),
            "user_click_rate_30d": _event_count(user_events_30d, "click") / event_denominator,
            "user_save_rate_30d": _event_count(user_events_30d, "save") / event_denominator,
            "user_apply_rate_30d": _event_count(user_events_30d, "apply") / event_denominator,
            "job_age_days": job_age_days,
            "job_skill_count": float(len(job.skills)),
            "job_required_skill_count": float(len(job.required_skills)),
            "job_impression_count_30d": float(_event_count(job_events_30d, "impression")),
            "job_click_count_30d": float(_event_count(job_events_30d, "click")),
            "job_save_count_30d": float(_event_count(job_events_30d, "save")),
            "job_apply_count_30d": float(_event_count(job_events_30d, "apply")),
            "job_popularity_30d": float(
                _event_count(job_events_30d, "click")
                + 3 * _event_count(job_events_30d, "save")
                + 5 * _event_count(job_events_30d, "apply")
            ),
            "skill_overlap_count": float(len(overlap)),
            "skill_overlap_ratio": len(overlap) / max(len(job.skills), 1),
            "required_skill_match_ratio": len(required_overlap) / len(job.required_skills) if job.required_skills else 1.0,
            "missing_required_skill_count": float(len(job.required_skills - candidate.skills)),
            "candidate_job_title_overlap": role_overlap,
            "target_role_exact_match": exact_role,
            "same_location": float(bool(_tokens(candidate.location) & _tokens(job.location))),
            "remote_compatible": self._remote_compatible(candidate.remote_preference, job.remote_mode),
            "retrieval_score": float(context.retrieval_score),
            "retrieval_position": float(max(context.retrieval_position, 0)),
        }
        self.schema.validate(values)
        return values

    def build_vector(self, candidate: CandidateSnapshot, job: JobSnapshot, context: FeatureContext) -> FeatureVector:
        return self.schema.vector(self.build(candidate, job, context))

    @staticmethod
    def _role_title_overlap(role: str, title: str) -> float:
        role_tokens = _tokens(role)
        title_tokens = _tokens(title)
        return len(role_tokens & title_tokens) / len(role_tokens) if role_tokens else 0.0

    @staticmethod
    def _remote_compatible(preference: str | None, remote_mode: str | None) -> float:
        if not preference or preference == "any":
            return 1.0
        return float(preference == remote_mode)

