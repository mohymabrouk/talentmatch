from typing import Literal

from pydantic import BaseModel, Field


EventType = Literal["impression", "click", "save", "dismiss", "apply"]


class InteractionCreate(BaseModel):
    job_id: str = Field(min_length=1, max_length=36)
    event_type: EventType
    recommendation_request_id: str = Field(min_length=1, max_length=36)


class InteractionResponse(BaseModel):
    id: str
    job_id: str
    event_type: EventType
    recommendation_request_id: str
    model_version: str

