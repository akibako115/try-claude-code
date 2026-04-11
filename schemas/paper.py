from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PaperCreate(BaseModel):
    title: str = Field(min_length=1)
    authors: str = ""
    url: str = ""
    memo: str = ""
    tags: str = ""
    auto_memo: bool = False


class PaperMemoUpdate(BaseModel):
    memo: str


class PaperTagsUpdate(BaseModel):
    tags: str


class PaperOut(BaseModel):
    id: int
    title: str
    authors: str
    url: str
    memo: str
    tags: str
    tags_list: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def populate_tags_list(self) -> PaperOut:
        self.tags_list = [t.strip() for t in self.tags.split(",") if t.strip()]
        return self


class PaperListOut(BaseModel):
    papers: list[PaperOut]
    all_tags: list[str]
    total: int
