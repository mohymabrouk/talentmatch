from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


RemotePreference = Literal["onsite", "hybrid", "remote", "any"]


def normalize_value(value: str) -> str:
    return " ".join(value.strip().split())


class ProfilePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_title: str | None = Field(default=None, max_length=160)
    target_roles: list[str] | None = Field(default=None, max_length=10)
    skills: list[str] | None = Field(default=None, max_length=50)
    years_experience: float | None = Field(default=None, ge=0, le=80)
    location: str | None = Field(default=None, max_length=160)
    remote_preference: RemotePreference | None = None
    minimum_salary: int | None = Field(default=None, ge=0, le=10_000_000)
    salary_currency: str | None = Field(default=None, min_length=3, max_length=8)

    @field_validator("target_roles", "skills")
    @classmethod
    def validate_strings(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        normalized = [normalize_value(value) for value in values]
        if any(not value for value in normalized):
            raise ValueError("values must not be blank")
        if len(set(value.casefold() for value in normalized)) != len(normalized):
            raise ValueError("values must be unique")
        return normalized


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    current_title: str | None = None
    target_roles: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    years_experience: float | None = None
    location: str | None = None
    remote_preference: RemotePreference | None = None
    minimum_salary: int | None = None
    salary_currency: str | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    company_name: str
    description: str
    location: str | None = None
    remote_mode: str | None = None
    seniority: str | None = None
    employment_type: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    source_url: str | None = None
    posted_at: datetime | None = None


class JobListResponse(BaseModel):
    items: list[JobResponse]
    page: int
    page_size: int
    total: int

