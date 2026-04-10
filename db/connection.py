from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "papers.db"


def utc_now_iso() -> str:
    """現在の UTC 時刻を ISO-8601 形式の文字列で返す。"""
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    """SQLite データベースに接続し、行ファクトリを設定して返す。"""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection
