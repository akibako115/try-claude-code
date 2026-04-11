from __future__ import annotations

from sqlalchemy.orm import Session

from models.paper import Paper


def _normalize_tags(tags_str: str) -> str:
    return ",".join(t.strip() for t in tags_str.split(",") if t.strip())


class PaperRepo:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_user(self, user_id: int, tag: str = "") -> list[Paper]:
        q = self._db.query(Paper).filter(Paper.user_id == user_id)
        if tag:
            q = q.filter(Paper.tags.like(f"%,{tag},%") | Paper.tags.like(f"{tag},%") | Paper.tags.like(f"%,{tag}") | (Paper.tags == tag))
        return q.order_by(Paper.created_at.desc(), Paper.id.desc()).all()

    def list_all_tags_by_user(self, user_id: int) -> list[str]:
        rows = (
            self._db.query(Paper.tags)
            .filter(Paper.user_id == user_id, Paper.tags != "")
            .all()
        )
        tag_set: set[str] = set()
        for (tags_str,) in rows:
            for t in tags_str.split(","):
                t = t.strip()
                if t:
                    tag_set.add(t)
        return sorted(tag_set)

    def get_by_id_and_user(self, paper_id: int, user_id: int) -> Paper | None:
        return (
            self._db.query(Paper)
            .filter(Paper.id == paper_id, Paper.user_id == user_id)
            .first()
        )

    def create(
        self,
        user_id: int,
        title: str,
        authors: str,
        url: str,
        memo: str,
        tags: str,
    ) -> Paper:
        paper = Paper(
            user_id=user_id,
            title=title,
            authors=authors,
            url=url,
            memo=memo,
            tags=_normalize_tags(tags),
        )
        self._db.add(paper)
        self._db.flush()
        return paper

    def update_memo(self, paper: Paper, memo: str) -> Paper:
        paper.memo = memo
        self._db.flush()
        return paper

    def update_tags(self, paper: Paper, tags: str) -> Paper:
        paper.tags = _normalize_tags(tags)
        self._db.flush()
        return paper

    def delete(self, paper: Paper) -> None:
        self._db.delete(paper)
        self._db.flush()
