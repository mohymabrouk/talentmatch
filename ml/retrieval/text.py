from collections.abc import Iterable


def candidate_text(
    target_roles: Iterable[str],
    skills: Iterable[str],
    years_experience: float | None,
    location: str | None,
    remote_preference: str | None,
) -> str:
    return "\n".join(
        [
            f"Target roles: {', '.join(target_roles)}",
            f"Skills: {', '.join(skills)}",
            f"Experience: {years_experience if years_experience is not None else 'not specified'} years",
            f"Location: {location or 'not specified'}",
            f"Work preference: {remote_preference or 'any'}",
        ]
    )


def job_text(job, skills: Iterable[str]) -> str:
    return "\n".join(
        [
            f"Title: {job.title}",
            f"Company: {job.company_name}",
            f"Location: {job.location or 'not specified'}",
            f"Work mode: {job.remote_mode or 'not specified'}",
            f"Seniority: {job.seniority or 'not specified'}",
            f"Skills: {', '.join(skills)}",
            f"Description: {job.description}",
        ]
    )

