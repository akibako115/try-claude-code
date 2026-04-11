from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import get_settings
from db.session import engine  # noqa: F401 — engine must be imported to configure alembic
from routers import auth as auth_router
from routers import papers as papers_router

BASE_DIR = Path(__file__).resolve().parent


def _run_migrations() -> None:
    """Alembic マイグレーションをプログラム的に実行する。"""
    from alembic import command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(str(BASE_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションのライフサイクル管理。"""
    _run_migrations()
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Paper Notes API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    origins = list({settings.frontend_origin, "http://localhost:5173"})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(papers_router.router, prefix="/api/v1/papers", tags=["papers"])

    # 本番ビルド: frontend/dist が存在すれば SPA として配信
    dist = BASE_DIR / "frontend" / "dist"
    if dist.exists():
        app.mount("/assets", StaticFiles(directory=str(dist / "assets")), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa_fallback(full_path: str) -> FileResponse:
            return FileResponse(dist / "index.html")

    return app


app = create_app()
