from datetime import datetime, timedelta

from app.core.config import Settings
from app.db.session import build_session_factory
from app.models import (
    CandidateProfile,
    CandidateSkill,
    CandidateTargetRole,
    Interaction,
    Job,
    JobSkill,
    RecommendationItem,
    RecommendationRequest,
    Skill,
    User,
)
from ml.features.builder import FeatureBuilder
from ml.features.dataset import FeatureDatasetBuilder
from ml.features.schema import FEATURE_SCHEMA, FEATURE_SCHEMA_VERSION
from ml.features.store import FeatureStore
from ml.features.types import CandidateSnapshot, FeatureContext, InteractionSnapshot, JobSnapshot


def test_feature_builder_excludes_future_behavior_and_clamps_future_job_age():
    as_of = datetime(2026, 1, 10, 12)
    candidate = CandidateSnapshot(
        user_id="user-1",
        current_title="ML Engineer",
        target_roles=("Machine Learning Engineer",),
        skills=frozenset({"python", "pytorch"}),
        years_experience=3,
        location="Paris, France",
        remote_preference="hybrid",
        interactions=(
            InteractionSnapshot("click", as_of - timedelta(days=5), "job-1"),
            InteractionSnapshot("save", as_of + timedelta(days=1), "job-1"),
        ),
    )
    job = JobSnapshot(
        job_id="job-1",
        title="Machine Learning Engineer",
        company_name="Acme",
        location="Paris, France",
        remote_mode="hybrid",
        seniority="mid",
        posted_at=as_of + timedelta(days=2),
        skills=frozenset({"python", "pytorch", "sql"}),
        required_skills=frozenset({"python", "pytorch"}),
        interactions=(InteractionSnapshot("apply", as_of + timedelta(days=1), "job-1"),),
    )

    values = FeatureBuilder().build(candidate, job, FeatureContext(as_of, 0.8, 2))

    assert values["user_interaction_count_30d"] == 1
    assert values["user_save_rate_30d"] == 0
    assert values["job_apply_count_30d"] == 0
    assert values["job_age_days"] == 0
    assert values["required_skill_match_ratio"] == 1
    assert values["target_role_exact_match"] == 1
    assert values["retrieval_position"] == 2


def test_training_and_serving_use_identical_versioned_features(tmp_path):
    settings = Settings(database_url=f"sqlite+pysqlite:///{tmp_path / 'features.db'}")
    _, factory = build_session_factory(settings)
    db = factory()
    served_at = datetime(2026, 1, 10, 12)
    user_id = "00000000-0000-0000-0000-000000000001"
    job_id = "00000000-0000-0000-0000-000000000002"
    request_id = "00000000-0000-0000-0000-000000000003"
    db.add(User(id=user_id, auth_provider_id="feature-test-user"))
    db.add(CandidateProfile(user_id=user_id, years_experience=3, location="Paris", remote_preference="hybrid"))
    skill = Skill(id="00000000-0000-0000-0000-000000000004", normalized="python", display_name="Python")
    db.add(skill)
    db.add(CandidateSkill(user_id=user_id, skill_id=skill.id))
    db.add(CandidateTargetRole(id="00000000-0000-0000-0000-000000000005", user_id=user_id, role_name="Python Engineer"))
    db.add(
        Job(
            id=job_id,
            external_id="feature-job",
            title="Python Engineer",
            company_name="Acme",
            description="Build Python services",
            location="Paris",
            remote_mode="hybrid",
            posted_at=served_at - timedelta(days=3),
            is_active=True,
        )
    )
    db.add(JobSkill(job_id=job_id, skill_id=skill.id, required=True))
    db.add(
        RecommendationRequest(
            id=request_id,
            user_id=user_id,
            model_version="content-v001",
            retrieval_version="retrieval-v001",
            candidate_count=1,
            returned_count=1,
            created_at=served_at,
        )
    )
    db.add(RecommendationItem(request_id=request_id, job_id=job_id, position=1, retrieval_score=0.75, ranking_score=0.8))
    db.add(
        Interaction(
            id="00000000-0000-0000-0000-000000000006",
            user_id=user_id,
            job_id=job_id,
            event_type="save",
            recommendation_request_id=request_id,
            model_version="content-v001",
            created_at=served_at + timedelta(hours=1),
        )
    )
    db.commit()

    rows = FeatureDatasetBuilder(db).build()
    serving_vector = FeatureStore(db, served_at).build(user_id, job_id, retrieval_score=0.75, retrieval_position=1)

    assert len(rows) == 1
    assert rows[0].label == 1
    assert rows[0].features == serving_vector
    assert rows[0].features.schema_version == FEATURE_SCHEMA_VERSION
    assert tuple(rows[0].features.names) == FEATURE_SCHEMA.names
    assert rows[0].features.as_dict()["user_save_rate_30d"] == 0
    db.close()

