"""Request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=4, max_length=200)


class ArticleIn(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    slug: str = Field(default="", max_length=200)
    deck: str = Field(default="", max_length=1000)
    body: str = Field(default="", max_length=120000)
    category_slug: str = Field(default="slovenija", max_length=64)
    author: str = Field(default="Uredništvo", max_length=120)
    image_url: str = Field(default="", max_length=500)
    image_caption: str = Field(default="", max_length=300)
    tags: list[str] = Field(default_factory=list)
    status: str = Field(default="published", pattern="^(published|draft)$")
    is_featured: bool = False
    is_breaking: bool = False
    is_live: bool = False
    published_at: str | None = None


class CategoryIn(BaseModel):
    slug: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=120)
    color: str = Field(default="#e01b22", max_length=20)
    description: str = Field(default="", max_length=500)
    sort: int = 0
    in_nav: bool = True


class SettingsIn(BaseModel):
    site_name: str = Field(default="Slovenec", max_length=80)
    site_tagline: str = Field(default="", max_length=160)
    site_email: str = Field(default="", max_length=160)
    site_city: str = Field(default="Ljubljana", max_length=80)
