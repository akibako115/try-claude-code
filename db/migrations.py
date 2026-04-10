from __future__ import annotations

import sqlite3

from db.connection import get_connection

LATEST_SCHEMA_VERSION = 3


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
    if "summary" in existing_columns:
        return 3
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


def migrate_to_v3(connection: sqlite3.Connection) -> None:
    """スキーマを v3 に移行する。"""
    if "summary" not in get_table_columns(connection, "papers"):
        connection.execute(
            "ALTER TABLE papers ADD COLUMN summary TEXT NOT NULL DEFAULT ''"
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

        if version == 2:
            migrate_to_v3(connection)
            set_schema_version(connection, 3)
            continue

        raise RuntimeError(f"Unsupported schema version: {version}")


def init_db() -> None:
    """データベースを初期化する。"""
    with get_connection() as connection:
        run_migrations(connection)
        connection.commit()
