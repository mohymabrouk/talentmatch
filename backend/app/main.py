from fastapi import FastAPI

from app.api.routes import health, jobs, profile
from app.config import Settings, get_settings
from app.db.session import build_session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    engine, session_factory = build_session_factory(app_settings)
    app = FastAPI(title="TalentMatch API", version="0.1.0")
    app.state.settings = app_settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.include_router(health.router, prefix=app_settings.api_prefix)
    app.include_router(profile.router, prefix=app_settings.api_prefix)
    app.include_router(jobs.router, prefix=app_settings.api_prefix)
    return app


app = create_app()

