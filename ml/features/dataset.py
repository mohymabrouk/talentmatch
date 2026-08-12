from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Interaction, RecommendationItem, RecommendationRequest
from ml.features.schema import FeatureVector
from ml.features.store import FeatureStore


@dataclass(frozen=True)
class TrainingRow:
    request_id: str
    user_id: str
    job_id: str
    served_at: datetime
    label: int
    features: FeatureVector

    def to_record(self) -> dict[str, object]:
        served_at = self.served_at
        if served_at.tzinfo is None:
            served_at = served_at.replace(tzinfo=UTC)
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "served_at": served_at.isoformat(),
            "label": self.label,
            **self.features.to_record(),
        }


class FeatureDatasetBuilder:
    """Builds served-item rows with feature values frozen at request creation time."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def build(self) -> list[TrainingRow]:
        rows: list[TrainingRow] = []
        requests = self.db.scalars(
            select(RecommendationRequest).order_by(RecommendationRequest.created_at, RecommendationRequest.id)
        ).all()
        for request in requests:
            items = self.db.scalars(
                select(RecommendationItem)
                .where(RecommendationItem.request_id == request.id)
                .order_by(RecommendationItem.position)
            ).all()
            events = self.db.scalars(
                select(Interaction).where(Interaction.recommendation_request_id == request.id)
            ).all()
            positive_jobs = {
                event.job_id
                for event in events
                if event.created_at >= request.created_at and event.event_type in {"save", "apply"}
            }
            store = FeatureStore(self.db, request.created_at)
            for item in items:
                rows.append(
                    TrainingRow(
                        request_id=request.id,
                        user_id=request.user_id,
                        job_id=item.job_id,
                        served_at=request.created_at,
                        label=int(item.job_id in positive_jobs),
                        features=store.build(
                            request.user_id,
                            item.job_id,
                            retrieval_score=float(item.retrieval_score or 0.0),
                            retrieval_position=item.position,
                        ),
                    )
                )
        return rows
