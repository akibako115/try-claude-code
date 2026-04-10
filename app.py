from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from db import init_db
from routers import papers as papers_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Paper Notes")

_templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
papers_router.set_templates(_templates)

app.include_router(papers_router.router)


@app.on_event("startup")
def on_startup() -> None:
    """アプリケーション起動時にデータベースを初期化する。"""
    init_db()
