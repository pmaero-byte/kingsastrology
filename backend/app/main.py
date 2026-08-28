from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from app.api.routes import router
from app.api.routes_api import router as api_router
from app.services.review_store import ReviewStore
from app.services.rule_loader import RuleRepository


def create_app() -> FastAPI:
    app = FastAPI(
        title="Kingsastrology Backend",
        version="0.1.0",
        description="Deterministic backend scoped to Brihat Jataka chapters 8-20.",
    )
    app.state.rule_repository = RuleRepository(_rules_dir())
    app.state.review_store = ReviewStore(_reviews_path())
    app.mount("/assets", StaticFiles(directory=_web_dir()), name="assets")
    app.include_router(router)
    app.include_router(api_router)

    @app.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse("/today", status_code=307)

    @app.get("/today")
    def today_page() -> FileResponse:
        return FileResponse(_web_dir() / "today.html")

    @app.get("/manifest.json")
    def manifest() -> FileResponse:
        return FileResponse(_web_dir() / "manifest.json")

    @app.get("/sw.js")
    def service_worker() -> FileResponse:
        return FileResponse(_web_dir() / "sw.js", headers={"Cache-Control": "no-cache"})

    @app.get("/app")
    def frontend_app() -> FileResponse:
        return FileResponse(_web_dir() / "index.html")

    @app.get("/clock")
    def spacetime_clock() -> FileResponse:
        return FileResponse(_web_dir() / "clock.html")

    @app.get("/mirror")
    def mirror_page() -> FileResponse:
        return FileResponse(_web_dir() / "mirror.html")

    @app.get("/tribunal")
    def tribunal_page() -> FileResponse:
        return FileResponse(_web_dir() / "tribunal.html")

    return app


def _rules_dir() -> Path:
    configured = os.getenv("KINGS_RULES_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "rules"


def _reviews_path() -> Path:
    configured = os.getenv("KINGS_RULE_REVIEWS")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[1] / "data" / "rule_reviews.json"


def _web_dir() -> Path:
    return Path(__file__).resolve().parent / "web"


app = create_app()
