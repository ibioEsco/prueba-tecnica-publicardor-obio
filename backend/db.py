import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from models import Base, Post

DEFAULT_SQLITE_URL = f"sqlite:///{Path(__file__).parent / 'posts.db'}"


def _database_url() -> str:
    """Resolve DATABASE_URL, normalising it to the psycopg3 driver.

    Supabase hands out `postgresql://...` (and older tooling `postgres://...`);
    SQLAlchemy would pick psycopg2 for both, which is not installed.
    Falls back to the local SQLite file when DATABASE_URL is unset.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return DEFAULT_SQLITE_URL
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def _engine_kwargs(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}

    kwargs: dict = {"pool_pre_ping": True}
    # Supabase's transaction pooler (port 6543) multiplexes several clients onto
    # one server connection, so it can hold neither a client-side pool nor
    # server-side prepared statements.
    if ":6543" in url:
        kwargs["poolclass"] = NullPool
        kwargs["connect_args"] = {"prepare_threshold": None}
    return kwargs


DATABASE_URL = _database_url()
engine = create_engine(DATABASE_URL, **_engine_kwargs(DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db():
    Base.metadata.create_all(engine)


def _iso(value: datetime) -> str:
    # SQLite gives back naive datetimes even for DateTime(timezone=True).
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _serialize(post: Post) -> dict:
    return {
        "id": post.id,
        "topic": post.topic,
        "language": post.language,
        "text": post.text,
        "image_url": post.image_url,
        "image_prompt": post.image_prompt,
        "viral_score": post.viral_score,
        "viral_reasons": post.viral_reasons or [],
        "status": post.status,
        "created_at": _iso(post.created_at),
        "updated_at": _iso(post.updated_at),
    }


def save_post(topic: str, language: str, text: str, image_url: str,
              image_prompt: str, viral_score: int, viral_reasons: list[str]) -> int:
    with SessionLocal() as session:
        post = Post(
            topic=topic,
            language=language,
            text=text,
            image_url=image_url,
            image_prompt=image_prompt,
            viral_score=viral_score,
            viral_reasons=list(viral_reasons),
            status="draft",
        )
        session.add(post)
        session.commit()
        return post.id


def _get(session: Session, post_id: int) -> Post | None:
    return session.scalar(select(Post).where(Post.id == post_id))


def update_post_status(post_id: int, status: str, text: str = None):
    with SessionLocal() as session:
        post = _get(session, post_id)
        if not post:
            return
        post.status = status
        if text:
            post.text = text
        session.commit()


def update_post_image(post_id: int, image_url: str, image_prompt: str):
    with SessionLocal() as session:
        post = _get(session, post_id)
        if not post:
            return
        post.image_url = image_url
        post.image_prompt = image_prompt
        session.commit()


def get_all_posts() -> list[dict]:
    with SessionLocal() as session:
        posts = session.scalars(
            select(Post).order_by(Post.created_at.desc(), Post.id.desc())
        ).all()
        return [_serialize(p) for p in posts]


def get_post(post_id: int) -> dict | None:
    with SessionLocal() as session:
        post = _get(session, post_id)
        return _serialize(post) if post else None
