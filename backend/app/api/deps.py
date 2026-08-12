from collections.abc import Generator
from uuid import UUID

from fastapi import Header, HTTPException, Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Generator[Session, None, None]:
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


def get_user_id(request: Request, x_demo_user_id: str | None = Header(default=None)) -> str:
    candidate = x_demo_user_id or request.app.state.settings.demo_user_id
    try:
        return str(UUID(candidate))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="X-Demo-User-ID must be a valid UUID") from exc
