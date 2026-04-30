from __future__ import annotations

from pydantic import BaseModel, Field


class SourceLink(BaseModel):
    url: str
    link_text: str
    link_type: str


class Section(BaseModel):
    canonical_id: str
    title: str
    commentary_text: str
    bible_references: list[str]
    links: list[SourceLink] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    places: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    author_claims: list[str] = Field(default_factory=list)


class DayDocument(BaseModel):
    source_url: str
    translation: str
    reading_plan_key: str
    semantic_date: None = None
    reading_refs: list[str]
    links: list[SourceLink]
    sections: list[Section]
    content_hash: str
