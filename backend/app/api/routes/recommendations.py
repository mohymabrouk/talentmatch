from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_user_id
from app.api.routes.profile import ensure_user
from app.models import Interaction, ModelVersion, RecommendationItem, RecommendationRequest
from app.schemas.recommendations import RecommendationItemResponse, RecommendationResponse
from app.services.recommendations import RecommendationService
from ml.features.schema import FEATURE_SCHEMA_VERSION

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    request: Request,
    limit: int = Query(default=20, ge=1, le=20),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    ensure_user(db, user_id)
    started = perf_counter()
    try:
        service = RecommendationService(db, request.app.state.settings)
        scored, candidate_count = service.recommend(user_id, limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    latency_ms = round((perf_counter() - started) * 1000)
    settings = request.app.state.settings
    model = db.query(ModelVersion).filter(ModelVersion.version == settings.model_version).one_or_none()
    if model is None:
        model = ModelVersion(
            model_type="content-retrieval",
            version=settings.model_version,
            status="active",
            artifact_path=settings.retrieval_artifact_dir,
        )
        db.add(model)
    recommendation_request = RecommendationRequest(
        user_id=user_id,
        model_version=settings.model_version,
        retrieval_version=settings.retrieval_version,
        candidate_count=candidate_count,
        returned_count=len(scored),
        latency_ms=latency_ms,
        fallback_used=service.fallback_used,
    )
    db.add(recommendation_request)
    db.flush()
    for position, item in enumerate(scored, start=1):
        db.add(
            RecommendationItem(
                request_id=recommendation_request.id,
                job_id=item.job.id,
                position=position,
                retrieval_score=item.retrieval_score,
                ranking_score=item.score,
            )
        )
        db.add(
            Interaction(
                user_id=user_id,
                job_id=item.job.id,
                event_type="impression",
                recommendation_request_id=recommendation_request.id,
                model_version=settings.model_version,
            )
        )
    db.commit()
    return RecommendationResponse(
        recommendation_request_id=recommendation_request.id,
        model_version=settings.model_version,
        retrieval_version=settings.retrieval_version,
        feature_schema_version=FEATURE_SCHEMA_VERSION,
        items=[
            RecommendationItemResponse(
                position=position,
                job_id=item.job.id,
                title=item.job.title,
                company=item.job.company_name,
                location=item.job.location,
                remote_mode=item.job.remote_mode,
                score=round(item.score, 6),
                match_reasons=item.reasons,
            )
            for position, item in enumerate(scored, start=1)
        ],
    )
