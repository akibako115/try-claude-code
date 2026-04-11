from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import Settings
from repositories.paper_repo import PaperRepo
from schemas.paper import (
    PaperCreate,
    PaperListOut,
    PaperMemoUpdate,
    PaperOut,
    PaperTagsUpdate,
)
from services.memo import generate_memo


class PaperService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self._repo = PaperRepo(db)
        self._db = db
        self._settings = settings

    def list_papers(self, user_id: int, tag: str = "") -> PaperListOut:
        papers = self._repo.list_by_user(user_id, tag)
        all_tags = self._repo.list_all_tags_by_user(user_id)
        return PaperListOut(
            papers=[PaperOut.model_validate(p) for p in papers],
            all_tags=all_tags,
            total=len(papers),
        )

    def create_paper(self, user_id: int, data: PaperCreate) -> PaperOut:
        memo = data.memo
        if data.auto_memo and not memo:
            memo = generate_memo(data.title, data.authors, data.url, self._settings.openai_api_key)

        paper = self._repo.create(
            user_id=user_id,
            title=data.title,
            authors=data.authors,
            url=data.url,
            memo=memo,
            tags=data.tags,
        )
        self._db.commit()
        self._db.refresh(paper)
        return PaperOut.model_validate(paper)

    def get_paper(self, user_id: int, paper_id: int) -> PaperOut:
        paper = self._repo.get_by_id_and_user(paper_id, user_id)
        if paper is None:
            raise HTTPException(status_code=404, detail="論文が見つかりません。")
        return PaperOut.model_validate(paper)

    def update_memo(self, user_id: int, paper_id: int, data: PaperMemoUpdate) -> PaperOut:
        paper = self._repo.get_by_id_and_user(paper_id, user_id)
        if paper is None:
            raise HTTPException(status_code=404, detail="論文が見つかりません。")
        self._repo.update_memo(paper, data.memo)
        self._db.commit()
        self._db.refresh(paper)
        return PaperOut.model_validate(paper)

    def update_tags(self, user_id: int, paper_id: int, data: PaperTagsUpdate) -> PaperOut:
        paper = self._repo.get_by_id_and_user(paper_id, user_id)
        if paper is None:
            raise HTTPException(status_code=404, detail="論文が見つかりません。")
        self._repo.update_tags(paper, data.tags)
        self._db.commit()
        self._db.refresh(paper)
        return PaperOut.model_validate(paper)

    def delete_paper(self, user_id: int, paper_id: int) -> None:
        paper = self._repo.get_by_id_and_user(paper_id, user_id)
        if paper is None:
            raise HTTPException(status_code=404, detail="論文が見つかりません。")
        self._repo.delete(paper)
        self._db.commit()
