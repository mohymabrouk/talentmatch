from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_user_id
from app.models import Interaction, Job, RecommendationItem, RecommendationRequest
from app.schemas.api import JobListResponse
from app.schemas.interactions import InteractionCreate, InteractionResponse

router = APIRouter(tags=["interactions"])


def list_user_jobs(db: Session, user_id: str, event_type: str, page: int, page_size: int) -> JobListResponse:
    rows = db.execute(
        select(Job, Interaction.created_at)
        .join(Interaction, Interaction.job_id == Job.id)
        .where(
            Interaction.user_id == user_id,
            Interaction.event_type == event_type,
            Job.is_active.is_(True),
        )
        .order_by(Interaction.created_at.desc(), Job.id)
    ).all()
    jobs: list[Job] = []
    seen: set[str] = set()
    for job, _created_at in rows:
        if job.id in seen:
            continue
        seen.add(job.id)
        jobs.append(job)
    start = (page - 1) * page_size
    return JobListResponse(
        items=jobs[start : start + page_size],
        page=page,
        page_size=page_size,
        total=len(jobs),
    )


@router.post("/interactions", response_model=InteractionResponse, status_code=201)
def create_interaction(
    payload: InteractionCreate,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
) -> InteractionResponse:
    job = db.scalar(select(Job).where(Job.id == payload.job_id, Job.is_active.is_(True)))
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    recommendation_request = db.scalar(
        select(RecommendationRequest).where(
            RecommendationRequest.id == payload.recommendation_request_id,
            RecommendationRequest.user_id == user_id,
        )
    )
    if recommendation_request is None:
        raise HTTPException(status_code=404, detail="Recommendation request not found")
    item = db.scalar(
        select(RecommendationItem).where(
            RecommendationItem.request_id == recommendation_request.id,
            RecommendationItem.job_id == payload.job_id,
        )
    )
    if item is None:
        raise HTTPException(status_code=400, detail="Job was not served in this recommendation request")
    interaction = Interaction(
        user_id=user_id,
        job_id=payload.job_id,
        event_type=payload.event_type,
        recommendation_request_id=recommendation_request.id,
        model_version=recommendation_request.model_version,
    )
    db.add(interaction)
    db.commit()
    return InteractionResponse(
        id=interaction.id,
        job_id=interaction.job_id,
        event_type=interaction.event_type,
        recommendation_request_id=interaction.recommendation_request_id,
        model_version=interaction.model_version,
    )


@router.get("/saved-jobs", response_model=JobListResponse)
def list_saved_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
) -> JobListResponse:
    return list_user_jobs(db, user_id, "save", page, page_size)


@router.get("/applications", response_model=JobListResponse)
def list_applications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
) -> JobListResponse:
    return list_user_jobs(db, user_id, "apply", page, page_size)
