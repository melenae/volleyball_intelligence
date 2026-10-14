import logging
from collections.abc import Generator
from typing import Literal

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

engine: Engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def database_status() -> Literal["ok", "unavailable"]:
    """Return ``ok`` when PostgreSQL answers ``SELECT 1``, otherwise ``unavailable``."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Database health check failed")
        return "unavailable"
    return "ok"


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
