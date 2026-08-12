from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_user_id
from app.config import get_settings
from app.db.models import CandidateProfile, CandidateSkill, CandidateTargetRole, Skill, User
from app.schemas.api import ProfilePatch, ProfileResponse

router = APIRouter(tags=["profile"])


def ensure_user(db: Session, user_id: str) -> User:
    user = db.get(User, user_id)
    if user is None:
        settings = get_settings()
        user = User(
            id=user_id,
            auth_provider_id=f"demo:{user_id}",
            email=settings.demo_user_email if user_id == settings.demo_user_id else None,
        )
        db.add(user)
        db.flush()
    return user


def profile_response(db: Session, user_id: str) -> ProfileResponse:
    profile = db.get(CandidateProfile, user_id)
    roles = db.scalars(
        select(CandidateTargetRole.role_name)
        .where(CandidateTargetRole.user_id == user_id)
        .order_by(CandidateTargetRole.priority, CandidateTargetRole.role_name)
    ).all()
    skills = db.scalars(
        select(Skill.display_name)
        .join(CandidateSkill, CandidateSkill.skill_id == Skill.id)
        .where(CandidateSkill.user_id == user_id)
        .order_by(Skill.display_name)
    ).all()
    return ProfileResponse(
        user_id=user_id,
        current_title=profile.current_title if profile else None,
        target_roles=list(roles),
        skills=list(skills),
        years_experience=profile.years_experience if profile else None,
        location=profile.location if profile else None,
        remote_preference=profile.remote_preference if profile else None,
        minimum_salary=profile.minimum_salary if profile else None,
        salary_currency=profile.salary_currency if profile else None,
    )


@router.get("/profile", response_model=ProfileResponse)
def get_profile(user_id: str = Depends(get_user_id), db: Session = Depends(get_db)) -> ProfileResponse:
    ensure_user(db, user_id)
    db.commit()
    return profile_response(db, user_id)


@router.patch("/profile", response_model=ProfileResponse)
def update_profile(
    payload: ProfilePatch,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    ensure_user(db, user_id)
    profile = db.get(CandidateProfile, user_id)
    if profile is None:
        profile = CandidateProfile(user_id=user_id)
        db.add(profile)
    for field in (
        "current_title",
        "years_experience",
        "location",
        "remote_preference",
        "minimum_salary",
        "salary_currency",
    ):
        value = getattr(payload, field)
        if value is not None:
            setattr(profile, field, value)

    if payload.target_roles is not None:
        db.execute(delete(CandidateTargetRole).where(CandidateTargetRole.user_id == user_id))
        db.add_all(
            [CandidateTargetRole(user_id=user_id, role_name=role, priority=index) for index, role in enumerate(payload.target_roles)]
        )
    if payload.skills is not None:
        db.execute(delete(CandidateSkill).where(CandidateSkill.user_id == user_id))
        for display_name in payload.skills:
            normalized = display_name.casefold()
            skill = db.scalar(select(Skill).where(Skill.normalized == normalized))
            if skill is None:
                skill = Skill(normalized=normalized, display_name=display_name)
                db.add(skill)
                db.flush()
            db.add(CandidateSkill(user_id=user_id, skill_id=skill.id))
    db.commit()
    return profile_response(db, user_id)

