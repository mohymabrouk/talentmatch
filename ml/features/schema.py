from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isfinite
from typing import Mapping


FEATURE_SCHEMA_VERSION = "features-v001"


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    dtype: str = "float32"
    description: str = ""


@dataclass(frozen=True)
class FeatureSchema:
    version: str
    definitions: tuple[FeatureDefinition, ...]

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def validate(self, values: Mapping[str, float]) -> None:
        expected = set(self.names)
        actual = set(values)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise ValueError(f"feature names do not match {self.version}; missing={missing}, extra={extra}")
        invalid = [name for name in self.names if not isfinite(float(values[name]))]
        if invalid:
            raise ValueError(f"features must be finite: {invalid}")

    def vector(self, values: Mapping[str, float]) -> "FeatureVector":
        self.validate(values)
        return FeatureVector(
            schema_version=self.version,
            names=self.names,
            values=tuple(float(values[name]) for name in self.names),
        )

    def as_dict(self) -> dict[str, object]:
        return {"version": self.version, "features": [asdict(item) for item in self.definitions]}

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2, sort_keys=True) + "\n"


@dataclass(frozen=True)
class FeatureVector:
    schema_version: str
    names: tuple[str, ...]
    values: tuple[float, ...]

    def as_dict(self) -> dict[str, float]:
        return dict(zip(self.names, self.values, strict=True))

    def to_record(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "features": self.as_dict()}


FEATURE_DEFINITIONS = (
    FeatureDefinition("user_years_experience", description="Candidate experience in years."),
    FeatureDefinition("user_skill_count", description="Number of normalized candidate skills."),
    FeatureDefinition("user_target_role_count", description="Number of target roles."),
    FeatureDefinition("user_interaction_count_7d", description="Candidate events in the trailing seven days."),
    FeatureDefinition("user_interaction_count_30d", description="Candidate events in the trailing 30 days."),
    FeatureDefinition("user_click_rate_30d", description="Candidate clicks divided by 30-day events."),
    FeatureDefinition("user_save_rate_30d", description="Candidate saves divided by 30-day events."),
    FeatureDefinition("user_apply_rate_30d", description="Candidate applies divided by 30-day events."),
    FeatureDefinition("job_age_days", description="Non-negative age of the job at the feature cutoff."),
    FeatureDefinition("job_skill_count", description="Number of normalized job skills."),
    FeatureDefinition("job_required_skill_count", description="Number of required job skills."),
    FeatureDefinition("job_impression_count_30d", description="Job impressions in the trailing 30 days."),
    FeatureDefinition("job_click_count_30d", description="Job clicks in the trailing 30 days."),
    FeatureDefinition("job_save_count_30d", description="Job saves in the trailing 30 days."),
    FeatureDefinition("job_apply_count_30d", description="Job applies in the trailing 30 days."),
    FeatureDefinition("job_popularity_30d", description="Clicks + 3 saves + 5 applies in 30 days."),
    FeatureDefinition("skill_overlap_count", description="Candidate skills present on the job."),
    FeatureDefinition("skill_overlap_ratio", description="Overlap divided by all job skills."),
    FeatureDefinition("required_skill_match_ratio", description="Required skills matched by the candidate."),
    FeatureDefinition("missing_required_skill_count", description="Required job skills absent from the candidate."),
    FeatureDefinition("candidate_job_title_overlap", description="Best target-role/title token overlap."),
    FeatureDefinition("target_role_exact_match", description="Whether a target role occurs in the job title."),
    FeatureDefinition("same_location", description="Whether candidate and job locations share a token."),
    FeatureDefinition("remote_compatible", description="Whether the job satisfies the work preference."),
    FeatureDefinition("retrieval_score", description="Cosine-like retrieval score at serving time."),
    FeatureDefinition("retrieval_position", description="One-based retrieval position, or zero if unavailable."),
)

FEATURE_SCHEMA = FeatureSchema(FEATURE_SCHEMA_VERSION, FEATURE_DEFINITIONS)

