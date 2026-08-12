#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import select  # noqa: E402

from app.core.config import Settings  # noqa: E402
from app.models import Job, JobSkill, Skill, User  # noqa: E402
from app.db.session import build_session_factory  # noqa: E402
from app.api.routes.profile import ensure_user  # noqa: E402


def parse_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def seed(path: Path, settings: Settings) -> int:
    _, factory = build_session_factory(settings)
    db = factory()
    try:
        ensure_user(db, settings.demo_user_id)
        count = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            job = db.scalar(select(Job).where(Job.external_id == record["external_id"]))
            if job is None:
                job = Job(external_id=record["external_id"])
                db.add(job)
            for field in (
                "title",
                "company_name",
                "description",
                "location",
                "remote_mode",
                "seniority",
                "employment_type",
                "salary_min",
                "salary_max",
                "salary_currency",
                "source",
                "source_url",
            ):
                setattr(job, field, record.get(field))
            job.posted_at = parse_datetime(record.get("posted_at"))
            job.is_active = True
            db.flush()
            existing_skill_ids = {
                skill_id for (skill_id,) in db.execute(select(JobSkill.skill_id).where(JobSkill.job_id == job.id))
            }
            for index, skill_record in enumerate(record.get("skills", [])):
                display_name = " ".join(skill_record["name"].split())
                normalized = display_name.casefold()
                skill = db.scalar(select(Skill).where(Skill.normalized == normalized))
                if skill is None:
                    skill = Skill(normalized=normalized, display_name=display_name)
                    db.add(skill)
                    db.flush()
                if skill.id not in existing_skill_ids:
                    db.add(
                        JobSkill(
                            job_id=job.id,
                            skill_id=skill.id,
                            required=bool(skill_record.get("required", False)),
                            weight=max(0.1, 1.0 - index * 0.05),
                        )
                    )
            count += 1
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    settings = Settings()
    dataset = Path(os.getenv("JOB_DATASET", Path(__file__).resolve().parents[1] / "data" / "jobs.jsonl"))
    print(f"Seeded {seed(dataset, settings)} jobs")
