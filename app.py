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
LATEST_SCHEMA_VERSION = 2

# FastAPI アプリのインスタンスを作成
app = FastAPI(title="Paper Notes")

# Jinja2 テンプレートのディレクトリを設定
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def utc_now_iso() -> str:
    """現在の UTC 時刻を ISO-8601 形式の文字列で返す。"""
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    """SQLite データベースに接続し、行ファクトリを設定して返す。"""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    """テーブルが存在するかどうかを確認する。"""
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def get_table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    """テーブルのカラムを取得する。"""
    return {
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }


def create_papers_table_v1(connection: sqlite3.Connection) -> None:
    """papers テーブルを作成する。"""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT NOT NULL DEFAULT '',
            url TEXT NOT NULL DEFAULT '',
            memo TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )


def infer_schema_version(connection: sqlite3.Connection) -> int:
    """スキーマのバージョンを推測する。"""
    if not table_exists(connection, "papers"):
        return 0

    existing_columns = get_table_columns(connection, "papers")
    if "tags" in existing_columns:
        return 2
    return 1


def ensure_schema_version_table(connection: sqlite3.Connection) -> None:
    """スキーマのバージョンテーブルを作成する。"""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        )
        """
    )
    row = connection.execute("SELECT version FROM schema_version").fetchone()
    if row is None:
        connection.execute(
            "INSERT INTO schema_version (version) VALUES (?)",
            (infer_schema_version(connection),),
        )


def get_schema_version(connection: sqlite3.Connection) -> int:
    """スキーマのバージョンを取得する。"""
    row = connection.execute("SELECT version FROM schema_version").fetchone()
    if row is None:
        raise RuntimeError("schema_version table is not initialized")
    return int(row[0])


def set_schema_version(connection: sqlite3.Connection, version: int) -> None:
    """スキーマのバージョンを設定する。"""
    connection.execute("UPDATE schema_version SET version = ?", (version,))


def migrate_to_v2(connection: sqlite3.Connection) -> None:
    """スキーマを v2 に移行する。"""
    if "tags" not in get_table_columns(connection, "papers"):
        connection.execute(
            "ALTER TABLE papers ADD COLUMN tags TEXT NOT NULL DEFAULT ''"
        )


def run_migrations(connection: sqlite3.Connection) -> None:
    """マイグレーションを実行する。"""
    ensure_schema_version_table(connection)

    while True:
        version = get_schema_version(connection)
        if version >= LATEST_SCHEMA_VERSION:
            return

        if version == 0:
            create_papers_table_v1(connection)
            set_schema_version(connection, 1)
            continue

        if version == 1:
            migrate_to_v2(connection)
            set_schema_version(connection, 2)
            continue

        raise RuntimeError(f"Unsupported schema version: {version}")


def init_db() -> None:
    """データベースを初期化する。"""
    with get_connection() as connection:
        run_migrations(connection)
        connection.commit()


def normalize_tags(tags_str: str) -> str:
    """カンマ区切りのタグ文字列を正規化（前後空白除去・空要素排除）して返す。"""
    return ",".join(t.strip() for t in tags_str.split(",") if t.strip())


def list_papers(tag: str = "") -> list[dict[str, Any]]:
    """論文をリストアップする。"""
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


def create_paper_record(
    title: str, authors: str, url: str, memo: str, tags: str
) -> int:
    """論文を作成する。"""
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
    """論文を取得する。"""
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
    """論文のメモを更新する。"""
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
    """論文のタグを更新する。"""
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
    """論文を削除する。"""
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Paper not found")


@app.on_event("startup")
def on_startup() -> None:
    """アプリケーション起動時にデータベースを初期化する。"""
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, tag: str = Query("")) -> HTMLResponse:
    """トップページを表示する。

    Args:
        request: リクエストオブジェクト
        tag: タグ
    Returns:
        HTMLResponse: トップページ
    """
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "papers": list_papers(tag),
            "all_tags": list_all_tags(),
            "active_tag": tag,
            "error": "",
            "form_data": {
                "title": "",
                "authors": "",
                "url": "",
                "memo": "",
                "tags": "",
            },
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
    """論文を作成する。

    Args:
        request: リクエストオブジェクト
        title: タイトル
        authors: 著者
        url: URL
        memo: メモ
        tags: タグ
    Returns:
        HTMLResponse: 論文を作成したページ
    """
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
            "form_data": {
                "title": "",
                "authors": "",
                "url": "",
                "memo": "",
                "tags": "",
            },
        },
    )


@app.post("/papers/{paper_id}/memo", response_class=HTMLResponse)
def save_memo(request: Request, paper_id: int, memo: str = Form("")) -> HTMLResponse:
    """論文のメモを保存する。

    Args:
        request: リクエストオブジェクト
        paper_id: 論文のID
        memo: メモ
    Returns:
        HTMLResponse: メモを保存した論文の詳細ページ
    """
    paper = update_paper_memo(paper_id, memo.strip())
    return templates.TemplateResponse(
        request,
        "partials/paper_item.html",
        {"paper": paper, "saved_memo": True, "saved_tags": False},
    )


@app.post("/papers/{paper_id}/tags", response_class=HTMLResponse)
def save_tags(request: Request, paper_id: int, tags: str = Form("")) -> HTMLResponse:
    """論文のタグを保存する。

    Args:
        request: リクエストオブジェクト
        paper_id: 論文のID
        tags: タグ
    Returns:
        HTMLResponse: タグを保存した論文の詳細ページ
    """
    paper = update_paper_tags(paper_id, tags.strip())
    return templates.TemplateResponse(
        request,
        "partials/paper_item.html",
        {"paper": paper, "saved_memo": False, "saved_tags": True},
    )


@app.post("/papers/{paper_id}/delete", response_class=HTMLResponse)
def delete_paper(request: Request, paper_id: int) -> HTMLResponse:
    """論文を削除する。

    Args:
        request: リクエストオブジェクト
        paper_id: 論文のID
    Returns:
        HTMLResponse: 論文を削除したページ
    """
    delete_paper_record(paper_id)
    return HTMLResponse("")
