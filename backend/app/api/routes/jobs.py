from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Job
from app.schemas.api import JobListResponse, JobResponse

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    location: str | None = Query(default=None, max_length=160),
    remote_mode: str | None = Query(default=None, pattern="^(onsite|hybrid|remote)$"),
    posted_after: datetime | None = None,
    db: Session = Depends(get_db),
) -> JobListResponse:
    query = select(Job).where(Job.is_active.is_(True))
    count_query = select(func.count()).select_from(Job).where(Job.is_active.is_(True))
    if location:
        condition = Job.location.ilike(f"%{location.strip()}%")
        query = query.where(condition)
        count_query = count_query.where(condition)
    if remote_mode:
        condition = Job.remote_mode == remote_mode
        query = query.where(condition)
        count_query = count_query.where(condition)
    if posted_after:
        condition = Job.posted_at >= posted_after
        query = query.where(condition)
        count_query = count_query.where(condition)
    total = db.scalar(count_query) or 0
    jobs = db.scalars(
        query.order_by(Job.posted_at.desc().nullslast(), Job.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return JobListResponse(items=jobs, page=page, page_size=page_size, total=total)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> Job:
    job = db.scalar(select(Job).where(Job.id == job_id, Job.is_active.is_(True)))
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

