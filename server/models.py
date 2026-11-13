"""SQLAlchemy models for the Slovenec news portal."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


class Category(Base):
    __tablename__ = "categories"

    slug: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="#e01b22")
    description: Mapped[str] = mapped_column(Text, default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    in_nav: Mapped[bool] = mapped_column(Boolean, default=True)

    articles: Mapped[list["Article"]] = relationship(back_populates="category")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(
        String(200), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    deck: Mapped[str] = mapped_column(Text, default="")
    body: Mapped[str] = mapped_column(Text, default="")
    category_slug: Mapped[str] = mapped_column(
        ForeignKey("categories.slug", ondelete="SET NULL"), nullable=True, index=True
    )
    author: Mapped[str] = mapped_column(String(120), default="Uredništvo")
    image_url: Mapped[str] = mapped_column(String(500), default="")
    image_caption: Mapped[str] = mapped_column(String(300), default="")
    tags: Mapped[str] = mapped_column(String(500), default="")  # comma separated
    status: Mapped[str] = mapped_column(String(20), default="published", index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_breaking: Mapped[bool] = mapped_column(Boolean, default=False)
    is_live: Mapped[bool] = mapped_column(Boolean, default=False)
    views: Mapped[int] = mapped_column(Integer, default=0)
    reading_minutes: Mapped[int] = mapped_column(Integer, default=3)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    category: Mapped[Category | None] = relationship(back_populates="articles")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), default="Urednik")
    password_hash: Mapped[str] = mapped_column(String(300), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")
