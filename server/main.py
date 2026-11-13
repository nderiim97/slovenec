"""Slovenec portal API and static site server.

Run locally:
    python -m uvicorn server.main:app --reload --port 8000
"""

from __future__ import annotations

import html
import logging
import re
import unicodedata
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from .config import BASE_DIR, settings
from .db import SessionLocal, get_db, init_db
from .models import AdminUser, Article, Category, Setting
from .schemas import ArticleIn, CategoryIn, LoginIn, SettingsIn
from .security import (
    COOKIE_NAME,
    SESSION_MAX_AGE,
    clear_login_attempts,
    client_ip,
    create_session_token,
    current_admin,
    login_allowed,
    register_failed_login,
    require_admin,
    verify_password,
)
from .seed import seed_database
from .serializers import article_dict, category_dict, get_settings

log = logging.getLogger("slovenec")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

PAGES = {
    "index.html",
    "category.html",
    "article.html",
    "search.html",
    "live.html",
    "admin.html",
    "404.html",
}

PUBLIC_DIR = BASE_DIR
COVERS_DIR = BASE_DIR / "assets" / "img" / "covers"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(title="Slovenec API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=PUBLIC_DIR / "assets"), name="assets")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:180] or "clanek"


def unique_slug(db: Session, base: str, article_id: int | None = None) -> str:
    slug = slugify(base)
    candidate = slug
    counter = 2
    while True:
        existing = db.scalar(select(Article).where(Article.slug == candidate))
        if existing is None or existing.id == article_id:
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1


def published_query():
    return (
        select(Article)
        .where(Article.status == "published")
        .options(selectinload(Article.category))
    )


def _meta_block(
    title: str,
    description: str,
    canonical: str,
    image: str = "",
    noindex: bool = False,
    jsonld: str = "",
) -> str:
    esc = html.escape
    origin = "{0.scheme}://{0.netloc}".format(urlsplit(canonical))
    image_url = image or f"{origin}/assets/img/covers/cover-1.svg"
    robots = (
        "noindex, nofollow" if noindex else "index, follow, max-image-preview:large"
    )
    parts = [
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(description[:300])}">',
        f'<meta name="robots" content="{robots}">',
        f'<link rel="canonical" href="{esc(canonical)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{esc(settings.site_name)}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description[:300])}">',
        f'<meta property="og:url" content="{esc(canonical)}">',
        f'<meta property="og:image" content="{esc(image_url)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(description[:300])}">',
        f'<meta name="twitter:image" content="{esc(image_url)}">',
    ]
    if jsonld:
        parts.append(f'<script type="application/ld+json">{jsonld}</script>')
    return "\n    ".join(parts)


def render_page(
    filename: str,
    *,
    title: str,
    description: str,
    canonical: str,
    image: str = "",
    noindex: bool = False,
    jsonld: str = "",
    status_code: int = 200,
) -> Response:
    if filename not in PAGES:
        raise HTTPException(status_code=404, detail="Stran ne obstaja.")
    source = (PUBLIC_DIR / filename).read_text(encoding="utf-8")
    meta = _meta_block(title, description, canonical, image, noindex, jsonld)
    page = source.replace("<!--seo-->", meta)
    return Response(
        content=page,
        status_code=status_code,
        media_type="text/html; charset=utf-8",
        headers={
            "Cache-Control": "no-store"
            if filename == "admin.html"
            else "public, max-age=60"
        },
    )


def site_meta(db: Session) -> dict[str, str]:
    return get_settings(db)


def base_url(request: Request) -> str:
    """Public origin used in canonical links, sitemap and structured data.

    In production the configured PUBLIC_BASE_URL wins (it may be behind a
    proxy). In local development the actual request host is used so the
    portal works on any port without editing .env.
    """
    if settings.environment == "production" and settings.public_base_url:
        return settings.public_base_url
    return str(request.base_url).rstrip("/")


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


@app.get("/", include_in_schema=False)
def home_page(request: Request, db: Session = Depends(get_db)):
    site = site_meta(db)
    return render_page(
        "index.html",
        title=f"{site['site_name']} — {site['site_tagline']}",
        description=(
            "Slovenski novičarski portal: dnevne novice, gospodarstvo, šport, kultura, "
            "mnenja in tehnologija. Neodvisno uredništvo, jasni viri."
        ),
        canonical=base_url(request) + "/",
    )


@app.get("/rubrika/{slug}", include_in_schema=False)
def category_page(slug: str, request: Request, db: Session = Depends(get_db)):
    category = db.get(Category, slug)
    if category is None:
        return render_page(
            "404.html",
            title="Stran ne obstaja — Slovenec",
            description="Iskane strani ni bilo mogoče najti.",
            canonical=base_url(request) + "/404",
            noindex=True,
            status_code=404,
        )
    site = site_meta(db)
    return render_page(
        "category.html",
        title=f"{category.name} — {site['site_name']}",
        description=category.description
        or f"Zadnje novice iz rubrike {category.name}.",
        canonical=f"{base_url(request)}/rubrika/{category.slug}",
    )


@app.get("/clanek/{slug}", include_in_schema=False)
def article_page(slug: str, request: Request, db: Session = Depends(get_db)):
    article = db.scalar(published_query().where(Article.slug == slug))
    if article is None:
        return render_page(
            "404.html",
            title="Članek ne obstaja — Slovenec",
            description="Iskanega članka ni bilo mogoče najti.",
            canonical=base_url(request) + "/404",
            noindex=True,
            status_code=404,
        )
    site = site_meta(db)
    canonical = f"{base_url(request)}/clanek/{article.slug}"
    image = (
        f"{base_url(request)}{article.image_url}"
        if article.image_url.startswith("/")
        else article.image_url
    )
    jsonld = (
        "{"
        '"@context":"https://schema.org",'
        '"@type":"NewsArticle",'
        f'"headline":{_json(article.title)},'
        f'"description":{_json(article.deck)},'
        f'"datePublished":{_json(article.published_at.isoformat() if article.published_at else "")},'
        f'"dateModified":{_json(article.updated_at.isoformat() if article.updated_at else "")},'
        f'"author":{{"@type":"Person","name":{_json(article.author)}}},'
        f'"publisher":{{"@type":"Organization","name":{_json(site["site_name"])}}},'
        f'"mainEntityOfPage":{_json(canonical)},'
        f'"image":[{_json(image)}]'
        "}"
    )
    return render_page(
        "article.html",
        title=f"{article.title} — {site['site_name']}",
        description=article.deck or article.title,
        canonical=canonical,
        image=image,
        jsonld=jsonld,
    )


def _json(value: str) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


@app.get("/iskanje", include_in_schema=False)
def search_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    site = site_meta(db)
    title = (
        f"Iskanje: {q} — {site['site_name']}" if q else f"Iskanje — {site['site_name']}"
    )
    return render_page(
        "search.html",
        title=title,
        description="Iskanje po arhivu portala Slovenec.",
        canonical=f"{base_url(request)}/iskanje",
        noindex=True,
    )


@app.get("/live", include_in_schema=False)
def live_page(request: Request, db: Session = Depends(get_db)):
    site = site_meta(db)
    return render_page(
        "live.html",
        title=f"V živo — {site['site_name']}",
        description="Neposredni prenosi in sprotno dogajanje.",
        canonical=f"{base_url(request)}/live",
    )


@app.get("/admin", include_in_schema=False)
def admin_page(request: Request):
    return render_page(
        "admin.html",
        title="Uredniški sistem — Slovenec",
        description="Uredniški sistem portala Slovenec.",
        canonical=f"{base_url(request)}/admin",
        noindex=True,
    )


@app.get("/404", include_in_schema=False)
def not_found_page(request: Request):
    return render_page(
        "404.html",
        title="Stran ne obstaja — Slovenec",
        description="Iskane strani ni bilo mogoče najti.",
        canonical=f"{base_url(request)}/404",
        noindex=True,
        status_code=404,
    )


@app.get("/robots.txt", include_in_schema=False)
def robots(request: Request):
    body = (
        "User-agent: *\n"
        "Disallow: /admin\n"
        "Disallow: /api/admin\n"
        f"Sitemap: {base_url(request)}/sitemap.xml\n"
    )
    return PlainTextResponse(body)


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap(request: Request, db: Session = Depends(get_db)):
    root = base_url(request)
    rows = db.scalars(
        select(Article)
        .where(Article.status == "published")
        .order_by(Article.published_at.desc())
    ).all()
    items = [
        f"<url><loc>{root}/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>"
    ]
    for category in db.scalars(select(Category).order_by(Category.sort)).all():
        items.append(
            f"<url><loc>{root}/rubrika/{category.slug}</loc>"
            "<changefreq>daily</changefreq><priority>0.8</priority></url>"
        )
    for article in rows:
        lastmod = article.updated_at.strftime("%Y-%m-%d") if article.updated_at else ""
        items.append(
            f"<url><loc>{root}/clanek/{article.slug}</loc>"
            f"<lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(items)
        + "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@app.get("/api/site")
def api_site(db: Session = Depends(get_db)):
    site = site_meta(db)
    counts = dict(
        db.execute(
            select(Article.category_slug, func.count(Article.id))
            .where(Article.status == "published")
            .group_by(Article.category_slug)
        ).all()
    )
    categories = db.scalars(select(Category).order_by(Category.sort)).all()
    return {
        "site": site,
        "categories": [category_dict(c, counts.get(c.slug, 0)) for c in categories],
    }


@app.get("/api/home")
def api_home(db: Session = Depends(get_db)):
    site = site_meta(db)
    now = datetime.now(timezone.utc)

    featured = db.scalars(
        published_query()
        .where(Article.is_featured.is_(True), Article.published_at <= now)
        .order_by(Article.published_at.desc())
        .limit(5)
    ).all()

    latest = db.scalars(
        published_query()
        .where(Article.published_at <= now)
        .order_by(Article.published_at.desc())
        .limit(14)
    ).all()

    if not featured:
        featured = latest[:5]

    most_read = db.scalars(
        published_query().order_by(Article.views.desc()).limit(6)
    ).all()

    breaking = db.scalars(
        published_query()
        .where(Article.is_breaking.is_(True), Article.published_at <= now)
        .order_by(Article.published_at.desc())
        .limit(4)
    ).all()

    live = db.scalars(
        published_query()
        .where(Article.is_live.is_(True), Article.published_at <= now)
        .order_by(Article.published_at.desc())
        .limit(3)
    ).all()

    categories = db.scalars(
        select(Category).where(Category.in_nav.is_(True)).order_by(Category.sort)
    ).all()

    sections = []
    for category in categories:
        rows = db.scalars(
            published_query()
            .where(Article.category_slug == category.slug, Article.published_at <= now)
            .order_by(Article.published_at.desc())
            .limit(4)
        ).all()
        if rows:
            sections.append(
                {
                    "category": category_dict(category),
                    "articles": [article_dict(a) for a in rows],
                }
            )

    opinions = db.scalars(
        published_query()
        .where(Article.category_slug == "mnenja")
        .order_by(Article.published_at.desc())
        .limit(4)
    ).all()

    lead = featured[0] if featured else (latest[0] if latest else None)
    return {
        "site": site,
        "lead": article_dict(lead) if lead else None,
        "featured": [article_dict(a) for a in featured[1:4]],
        "latest": [article_dict(a) for a in latest],
        "most_read": [article_dict(a) for a in most_read],
        "breaking": [article_dict(a) for a in breaking],
        "live": [article_dict(a) for a in live],
        "sections": sections,
        "opinions": [article_dict(a) for a in opinions],
    }


@app.get("/api/articles")
def api_articles(
    db: Session = Depends(get_db),
    category: str | None = None,
    q: str | None = None,
    limit: int = 12,
    offset: int = 0,
    sort: str = "newest",
):
    limit = max(1, min(limit, 50))
    offset = max(0, offset)
    stmt = published_query().where(Article.published_at <= datetime.now(timezone.utc))

    if category:
        stmt = stmt.where(Article.category_slug == category)
    if q:
        needle = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Article.title.ilike(needle),
                Article.deck.ilike(needle),
                Article.body.ilike(needle),
                Article.tags.ilike(needle),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0

    if sort == "oldest":
        stmt = stmt.order_by(Article.published_at.asc())
    elif sort == "popular":
        stmt = stmt.order_by(Article.views.desc())
    else:
        stmt = stmt.order_by(Article.published_at.desc())

    rows = db.scalars(stmt.offset(offset).limit(limit)).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "articles": [article_dict(a) for a in rows],
    }


@app.get("/api/articles/{slug}")
def api_article(slug: str, db: Session = Depends(get_db)):
    article = db.scalar(published_query().where(Article.slug == slug))
    if article is None:
        raise HTTPException(status_code=404, detail="Članek ne obstaja.")

    related = db.scalars(
        published_query()
        .where(
            Article.category_slug == article.category_slug,
            Article.id != article.id,
            Article.status == "published",
        )
        .order_by(Article.published_at.desc())
        .limit(4)
    ).all()

    prev_article = db.scalar(
        published_query()
        .where(Article.published_at < article.published_at)
        .order_by(Article.published_at.desc())
        .limit(1)
    )
    next_article = db.scalar(
        published_query()
        .where(Article.published_at > article.published_at)
        .order_by(Article.published_at.asc())
        .limit(1)
    )

    return {
        "article": article_dict(article, full=True),
        "related": [article_dict(a) for a in related],
        "prev": article_dict(prev_article) if prev_article else None,
        "next": article_dict(next_article) if next_article else None,
    }


@app.post("/api/articles/{slug}/view")
def api_article_view(slug: str, db: Session = Depends(get_db)):
    article = db.scalar(select(Article).where(Article.slug == slug))
    if article is None:
        raise HTTPException(status_code=404, detail="Članek ne obstaja.")
    article.views = (article.views or 0) + 1
    db.commit()
    return {"views": article.views}


@app.get("/api/live")
def api_live(db: Session = Depends(get_db)):
    rows = db.scalars(
        published_query()
        .where(Article.is_live.is_(True))
        .order_by(Article.published_at.desc())
    ).all()
    return {"articles": [article_dict(a) for a in rows]}


# ---------------------------------------------------------------------------
# Admin API
# ---------------------------------------------------------------------------


@app.post("/api/admin/login")
def admin_login(
    payload: LoginIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    ip = client_ip(request)
    if not login_allowed(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Preveč poskusov. Poskusite znova čez 15 minut.",
        )
    user = db.scalar(
        select(AdminUser).where(AdminUser.email == payload.email.strip().lower())
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        register_failed_login(ip)
        raise HTTPException(status_code=401, detail="Napačen e-naslov ali geslo.")
    clear_login_attempts(ip)
    response.set_cookie(
        COOKIE_NAME,
        create_session_token(user.id),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.environment == "production",
        path="/",
    )
    return {"user": {"id": user.id, "email": user.email, "name": user.name}}


@app.post("/api/admin/logout")
def admin_logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


@app.get("/api/admin/me")
def admin_me(admin: AdminUser | None = Depends(current_admin)):
    if admin is None:
        return {"user": None}
    return {"user": {"id": admin.id, "email": admin.email, "name": admin.name}}


@app.get("/api/admin/stats")
def admin_stats(
    admin: AdminUser = Depends(require_admin), db: Session = Depends(get_db)
):
    total = db.scalar(select(func.count()).select_from(Article)) or 0
    published = (
        db.scalar(
            select(func.count())
            .select_from(Article)
            .where(Article.status == "published")
        )
        or 0
    )
    drafts = total - published
    views = db.scalar(select(func.coalesce(func.sum(Article.views), 0))) or 0
    categories = db.scalar(select(func.count()).select_from(Category)) or 0
    recent = db.scalars(
        select(Article).order_by(Article.updated_at.desc()).limit(5)
    ).all()
    return {
        "total": total,
        "published": published,
        "drafts": drafts,
        "views": int(views),
        "categories": categories,
        "recent": [article_dict(a) for a in recent],
    }


@app.get("/api/admin/articles")
def admin_articles(
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
    q: str = "",
    status_filter: str = "",
    limit: int = 100,
    offset: int = 0,
):
    stmt = select(Article).options(selectinload(Article.category))
    if q:
        needle = f"%{q.strip()}%"
        stmt = stmt.where(or_(Article.title.ilike(needle), Article.slug.ilike(needle)))
    if status_filter in {"published", "draft"}:
        stmt = stmt.where(Article.status == status_filter)
    total = (
        db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    )
    rows = db.scalars(
        stmt.order_by(Article.published_at.desc())
        .offset(max(0, offset))
        .limit(min(limit, 200))
    ).all()
    return {"total": total, "articles": [article_dict(a, full=True) for a in rows]}


@app.post("/api/admin/articles", status_code=201)
def admin_create_article(
    payload: ArticleIn,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if db.get(Category, payload.category_slug) is None:
        raise HTTPException(status_code=400, detail="Kategorija ne obstaja.")
    article = Article(
        slug=unique_slug(db, payload.slug or payload.title),
        title=payload.title.strip(),
        deck=payload.deck.strip(),
        body=payload.body.strip(),
        category_slug=payload.category_slug,
        author=payload.author.strip() or "Uredništvo",
        image_url=payload.image_url.strip(),
        image_caption=payload.image_caption.strip(),
        tags=",".join(t.strip() for t in payload.tags if t.strip()),
        status=payload.status,
        is_featured=payload.is_featured,
        is_breaking=payload.is_breaking,
        is_live=payload.is_live,
        reading_minutes=max(1, round(len(payload.body.split()) / 200)),
        published_at=_parse_datetime(payload.published_at),
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article_dict(article, full=True)


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return datetime.now(timezone.utc)


@app.put("/api/admin/articles/{article_id}")
def admin_update_article(
    article_id: int,
    payload: ArticleIn,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Članek ne obstaja.")
    if db.get(Category, payload.category_slug) is None:
        raise HTTPException(status_code=400, detail="Kategorija ne obstaja.")
    article.title = payload.title.strip()
    article.slug = unique_slug(db, payload.slug or payload.title, article_id=article.id)
    article.deck = payload.deck.strip()
    article.body = payload.body.strip()
    article.category_slug = payload.category_slug
    article.author = payload.author.strip() or "Uredništvo"
    article.image_url = payload.image_url.strip()
    article.image_caption = payload.image_caption.strip()
    article.tags = ",".join(t.strip() for t in payload.tags if t.strip())
    article.status = payload.status
    article.is_featured = payload.is_featured
    article.is_breaking = payload.is_breaking
    article.is_live = payload.is_live
    article.reading_minutes = max(1, round(len(payload.body.split()) / 200))
    article.published_at = _parse_datetime(payload.published_at)
    db.commit()
    db.refresh(article)
    return article_dict(article, full=True)


@app.delete("/api/admin/articles/{article_id}")
def admin_delete_article(
    article_id: int,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Članek ne obstaja.")
    db.delete(article)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/categories")
def admin_categories(
    admin: AdminUser = Depends(require_admin), db: Session = Depends(get_db)
):
    counts = dict(
        db.execute(
            select(Article.category_slug, func.count(Article.id)).group_by(
                Article.category_slug
            )
        ).all()
    )
    rows = db.scalars(select(Category).order_by(Category.sort)).all()
    return {"categories": [category_dict(c, counts.get(c.slug, 0)) for c in rows]}


@app.post("/api/admin/categories", status_code=201)
def admin_create_category(
    payload: CategoryIn,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    slug = slugify(payload.slug)
    if db.get(Category, slug) is not None:
        raise HTTPException(
            status_code=409, detail="Kategorija s tem slugom že obstaja."
        )
    category = Category(
        slug=slug,
        name=payload.name.strip(),
        color=payload.color,
        description=payload.description,
        sort=payload.sort,
        in_nav=payload.in_nav,
    )
    db.add(category)
    db.commit()
    return category_dict(category, 0)


@app.put("/api/admin/categories/{slug}")
def admin_update_category(
    slug: str,
    payload: CategoryIn,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    category = db.get(Category, slug)
    if category is None:
        raise HTTPException(status_code=404, detail="Kategorija ne obstaja.")
    category.name = payload.name.strip()
    category.color = payload.color
    category.description = payload.description
    category.sort = payload.sort
    category.in_nav = payload.in_nav
    db.commit()
    return category_dict(category)


@app.delete("/api/admin/categories/{slug}")
def admin_delete_category(
    slug: str,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    category = db.get(Category, slug)
    if category is None:
        raise HTTPException(status_code=404, detail="Kategorija ne obstaja.")
    used = (
        db.scalar(
            select(func.count())
            .select_from(Article)
            .where(Article.category_slug == slug)
        )
        or 0
    )
    if used:
        raise HTTPException(status_code=409, detail="Kategorija vsebuje članke.")
    db.delete(category)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/settings")
def admin_get_settings(
    admin: AdminUser = Depends(require_admin), db: Session = Depends(get_db)
):
    return {"settings": get_settings(db)}


@app.put("/api/admin/settings")
def admin_put_settings(
    payload: SettingsIn,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    values = payload.model_dump()
    for key, value in values.items():
        row = db.get(Setting, key)
        if row is None:
            db.add(Setting(key=key, value=str(value)))
        else:
            row.value = str(value)
    db.commit()
    return {"settings": get_settings(db)}


@app.get("/health")
def health():
    return {"ok": True, "app": settings.app_name}
