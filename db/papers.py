from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from db.connection import get_connection, utc_now_iso


def normalize_tags(tags_str: str) -> str:
    """カンマ区切りのタグ文字列を正規化（前後空白除去・空要素排除）して返す。"""
    return ",".join(t.strip() for t in tags_str.split(",") if t.strip())


def list_papers(tag: str = "") -> list[dict[str, Any]]:
    """論文をリストアップする。"""
    with get_connection() as connection:
        if tag:
            rows = connection.execute(
                """
                SELECT id, title, authors, url, memo, summary, tags, created_at, updated_at
                FROM papers
                WHERE (',' || tags || ',') LIKE ?
                ORDER BY created_at DESC, id DESC
                """,
                (f"%,{tag},%",),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, title, authors, url, memo, summary, tags, created_at, updated_at
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
    title: str, authors: str, url: str, memo: str, tags: str, summary: str = ""
) -> int:
    """論文を作成する。"""
    timestamp = utc_now_iso()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO papers (title, authors, url, memo, summary, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, authors, url, memo, summary, normalize_tags(tags), timestamp, timestamp),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_paper(paper_id: int) -> dict[str, Any]:
    """論文を取得する。"""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, authors, url, memo, summary, tags, created_at, updated_at
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
