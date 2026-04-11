from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import get_settings
from db.session import Base, engine
from routers import auth as auth_router
from routers import papers as papers_router

BASE_DIR = Path(__file__).resolve().parent


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Paper Notes API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin, "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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


def _init_db() -> None:
    """テーブルが存在しない場合に自動作成する（Alembic 未使用時のフォールバック）。"""
    # models を import して Base.metadata に登録する
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


app = create_app()


@app.on_event("startup")
def on_startup() -> None:
    """アプリケーション起動時にデータベーステーブルを確認・作成する。"""
    _init_db()
