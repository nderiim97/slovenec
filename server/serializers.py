"""Dictionary serializers shared by the public and admin APIs."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .models import Article, Category, Setting


def get_settings(db: Session) -> dict[str, str]:
    values = {
        "site_name": settings.site_name,
        "site_tagline": settings.site_tagline,
        "site_email": settings.site_email,
        "site_city": settings.site_city,
    }
    for row in db.scalars(select(Setting)).all():
        values[row.key] = row.value
    return values


def category_dict(category: Category, count: int | None = None) -> dict:
    data = {
        "slug": category.slug,
        "name": category.name,
        "color": category.color,
        "description": category.description,
        "sort": category.sort,
        "in_nav": category.in_nav,
    }
    if count is not None:
        data["article_count"] = count
    return data


def article_dict(article: Article, full: bool = False) -> dict:
    data = {
        "id": article.id,
        "slug": article.slug,
        "title": article.title,
        "deck": article.deck,
        "category_slug": article.category_slug,
        "category_name": article.category.name if article.category else "",
        "category_color": article.category.color if article.category else "#e01b22",
        "author": article.author,
        "image_url": article.image_url,
        "image_caption": article.image_caption,
        "tags": [t.strip() for t in (article.tags or "").split(",") if t.strip()],
        "is_featured": article.is_featured,
        "is_breaking": article.is_breaking,
        "is_live": article.is_live,
        "views": article.views,
        "reading_minutes": article.reading_minutes,
        "status": article.status,
        "published_at": article.published_at.isoformat()
        if article.published_at
        else None,
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
        "url": f"/clanek/{article.slug}",
    }
    if full:
        data["body"] = article.body
        data["created_at"] = (
            article.created_at.isoformat() if article.created_at else None
        )
    return data
