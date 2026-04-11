from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from config import Settings, get_settings
from db.session import get_db
from dependencies import get_current_user
from models.user import User
from schemas.paper import (
    PaperCreate,
    PaperListOut,
    PaperMemoUpdate,
    PaperOut,
    PaperTagsUpdate,
)
from services.paper_service import PaperService

router = APIRouter()


@router.get("/", response_model=PaperListOut)
def list_papers(
    tag: str = Query(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PaperListOut:
    """ログイン中ユーザーの論文一覧を返す。タグでフィルタ可能。"""
    return PaperService(db, settings).list_papers(current_user.id, tag)


@router.post("/", response_model=PaperOut, status_code=201)
def create_paper(
    data: PaperCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PaperOut:
    """論文を新規作成する。"""
    return PaperService(db, settings).create_paper(current_user.id, data)


@router.get("/{paper_id}", response_model=PaperOut)
def get_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PaperOut:
    """指定した論文を取得する。"""
    return PaperService(db, settings).get_paper(current_user.id, paper_id)


@router.patch("/{paper_id}/memo", response_model=PaperOut)
def update_memo(
    paper_id: int,
    data: PaperMemoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PaperOut:
    """論文のメモを更新する。"""
    return PaperService(db, settings).update_memo(current_user.id, paper_id, data)


@router.patch("/{paper_id}/tags", response_model=PaperOut)
def update_tags(
    paper_id: int,
    data: PaperTagsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PaperOut:
    """論文のタグを更新する。"""
    return PaperService(db, settings).update_tags(current_user.id, paper_id, data)


@router.delete("/{paper_id}", status_code=204)
def delete_paper(
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Response:
    """論文を削除する。"""
    PaperService(db, settings).delete_paper(current_user.id, paper_id)
    return Response(status_code=204)
