from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "papers.db"

app = FastAPI(title="Paper Notes")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                authors TEXT NOT NULL DEFAULT '',
                url TEXT NOT NULL DEFAULT '',
                memo TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        # 既存DBへのマイグレーション: tagsカラムが無ければ追加
        existing_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(papers)").fetchall()
        }
        if "tags" not in existing_columns:
            connection.execute("ALTER TABLE papers ADD COLUMN tags TEXT NOT NULL DEFAULT ''")
        connection.commit()


def normalize_tags(tags_str: str) -> str:
    """カンマ区切りのタグ文字列を正規化（前後空白除去・空要素排除）して返す。"""
    return ",".join(t.strip() for t in tags_str.split(",") if t.strip())


def list_papers(tag: str = "") -> list[dict[str, Any]]:
    with get_connection() as connection:
        if tag:
            rows = connection.execute(
                """
                SELECT id, title, authors, url, memo, tags, created_at, updated_at
                FROM papers
                WHERE (',' || tags || ',') LIKE ?
                ORDER BY created_at DESC, id DESC
                """,
                (f"%,{tag},%",),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, title, authors, url, memo, tags, created_at, updated_at
                FROM papers
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()
    return [dict(row) for row in rows]


def list_all_tags() -> list[str]:
    """全論文のタグをまとめて重複排除・ソートして返す。"""
    with get_connection() as connection:
        rows = connection.execute("SELECT tags FROM papers WHERE tags != ''").fetchall()
    tag_set: set[str] = set()
    for row in rows:
        for t in row["tags"].split(","):
            t = t.strip()
            if t:
                tag_set.add(t)
    return sorted(tag_set)


def create_paper_record(title: str, authors: str, url: str, memo: str, tags: str) -> int:
    timestamp = utc_now_iso()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO papers (title, authors, url, memo, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (title, authors, url, memo, normalize_tags(tags), timestamp, timestamp),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_paper(paper_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, authors, url, memo, tags, created_at, updated_at
            FROM papers
            WHERE id = ?
            """,
            (paper_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return dict(row)


def update_paper_memo(paper_id: int, memo: str) -> dict[str, Any]:
    timestamp = utc_now_iso()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE papers
            SET memo = ?, updated_at = ?
            WHERE id = ?
            """,
            (memo, timestamp, paper_id),
        )
        connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Paper not found")
    return get_paper(paper_id)


def update_paper_tags(paper_id: int, tags: str) -> dict[str, Any]:
    timestamp = utc_now_iso()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE papers
            SET tags = ?, updated_at = ?
            WHERE id = ?
            """,
            (normalize_tags(tags), timestamp, paper_id),
        )
        connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Paper not found")
    return get_paper(paper_id)


def delete_paper_record(paper_id: int) -> None:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Paper not found")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, tag: str = Query("")) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "papers": list_papers(tag),
            "all_tags": list_all_tags(),
            "active_tag": tag,
            "error": "",
            "form_data": {"title": "", "authors": "", "url": "", "memo": "", "tags": ""},
        },
    )


@app.post("/papers", response_class=HTMLResponse)
def create_paper(
    request: Request,
    title: str = Form(""),
    authors: str = Form(""),
    url: str = Form(""),
    memo: str = Form(""),
    tags: str = Form(""),
) -> HTMLResponse:
    clean_title = title.strip()
    form_data = {
        "title": clean_title,
        "authors": authors.strip(),
        "url": url.strip(),
        "memo": memo.strip(),
        "tags": tags.strip(),
    }
    if not clean_title:
        return templates.TemplateResponse(
            request,
            "partials/page_content.html",
            {
                "papers": list_papers(),
                "all_tags": list_all_tags(),
                "active_tag": "",
                "error": "タイトルは必須です。",
                "form_data": form_data,
            },
            status_code=422,
        )

    create_paper_record(**form_data)
    return templates.TemplateResponse(
        request,
        "partials/page_content.html",
        {
            "papers": list_papers(),
            "all_tags": list_all_tags(),
            "active_tag": "",
            "error": "",
            "form_data": {"title": "", "authors": "", "url": "", "memo": "", "tags": ""},
        },
    )


@app.post("/papers/{paper_id}/memo", response_class=HTMLResponse)
def save_memo(request: Request, paper_id: int, memo: str = Form("")) -> HTMLResponse:
    paper = update_paper_memo(paper_id, memo.strip())
    return templates.TemplateResponse(
        request,
        "partials/paper_item.html",
        {"paper": paper, "saved": True},
    )


@app.post("/papers/{paper_id}/tags", response_class=HTMLResponse)
def save_tags(request: Request, paper_id: int, tags: str = Form("")) -> HTMLResponse:
    paper = update_paper_tags(paper_id, tags.strip())
    return templates.TemplateResponse(
        request,
        "partials/paper_item.html",
        {"paper": paper, "saved": True},
    )


@app.post("/papers/{paper_id}/delete", response_class=HTMLResponse)
def delete_paper(request: Request, paper_id: int) -> HTMLResponse:
    delete_paper_record(paper_id)
    return HTMLResponse("")
