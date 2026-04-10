from __future__ import annotations

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.papers import (
    create_paper_record,
    delete_paper_record,
    list_all_tags,
    list_papers,
    update_paper_memo,
    update_paper_tags,
)
from services.memo import generate_memo

router = APIRouter()
templates: Jinja2Templates


def set_templates(t: Jinja2Templates) -> None:
    """テンプレートエンジンを設定する。"""
    global templates
    templates = t


@router.get("/", response_class=HTMLResponse)
def index(request: Request, tag: str = Query("")) -> HTMLResponse:
    """トップページを表示する。"""
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
                "auto_summary": False,
            },
        },
    )


@router.post("/papers", response_class=HTMLResponse)
def create_paper(
    request: Request,
    title: str = Form(""),
    authors: str = Form(""),
    url: str = Form(""),
    memo: str = Form(""),
    tags: str = Form(""),
    auto_summary: bool = Form(False),
) -> HTMLResponse:
    """論文を作成する。"""
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
                "form_data": {**form_data, "auto_summary": auto_summary},
            },
            status_code=422,
        )

    if auto_summary and not form_data["memo"]:
        form_data["memo"] = generate_memo(
            form_data["title"], form_data["authors"], form_data["url"]
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
                "auto_summary": False,
            },
        },
    )


@router.post("/papers/{paper_id}/memo", response_class=HTMLResponse)
def save_memo(request: Request, paper_id: int, memo: str = Form("")) -> HTMLResponse:
    """論文のメモを保存する。"""
    paper = update_paper_memo(paper_id, memo.strip())
    return templates.TemplateResponse(
        request,
        "partials/paper_item.html",
        {"paper": paper, "saved_memo": True, "saved_tags": False},
    )


@router.post("/papers/{paper_id}/tags", response_class=HTMLResponse)
def save_tags(request: Request, paper_id: int, tags: str = Form("")) -> HTMLResponse:
    """論文のタグを保存する。"""
    paper = update_paper_tags(paper_id, tags.strip())
    return templates.TemplateResponse(
        request,
        "partials/paper_item.html",
        {"paper": paper, "saved_memo": False, "saved_tags": True},
    )


@router.post("/papers/{paper_id}/delete", response_class=HTMLResponse)
def delete_paper(request: Request, paper_id: int) -> HTMLResponse:
    """論文を削除する。"""
    delete_paper_record(paper_id)
    return HTMLResponse("")
