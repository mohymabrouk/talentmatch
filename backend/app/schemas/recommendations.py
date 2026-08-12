from pydantic import BaseModel, Field


class RecommendationItemResponse(BaseModel):
    position: int
    job_id: str
    title: str
    company: str
    location: str | None = None
    remote_mode: str | None = None
    score: float = Field(ge=0, le=1)
    match_reasons: list[str]


class RecommendationResponse(BaseModel):
    recommendation_request_id: str
    model_version: str
    retrieval_version: str
    items: list[RecommendationItemResponse]

