from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_user_id
from app.db.models import Interaction, Job, RecommendationItem, RecommendationRequest
from app.schemas.interactions import InteractionCreate, InteractionResponse

router = APIRouter(tags=["interactions"])


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

