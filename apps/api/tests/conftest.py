from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models import Base


def _ensure_test_database(url: str) -> None:
    parsed = make_url(url)
    admin_url = parsed.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    db_name = parsed.database
    if not db_name:
        raise RuntimeError("TEST database URL must include a database name")
    with admin_engine.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{db_name}"'))


def _run_migrations(database_url: str) -> None:
    os.environ["DATABASE_URL"] = database_url
    get_settings.cache_clear()
    config = Config("alembic.ini")
    config.set_main_option("script_location", "migrations")
    command.upgrade(config, "head")
    get_settings.cache_clear()


def _truncate_all(engine: Engine) -> None:
    table_names = ", ".join(f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables))
    if not table_names:
        return
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session")
def postgres_engine() -> Generator[Engine, None, None]:
    settings = get_settings()
    database_url = os.environ.get("TEST_DATABASE_URL", settings.test_database_url)
    try:
        _ensure_test_database(database_url)
        _run_migrations(database_url)
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL unavailable for integration tests: {exc}")
        raise
    yield engine
    engine.dispose()
    get_settings.cache_clear()


@pytest.fixture
def db_session(postgres_engine: Engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=postgres_engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        _truncate_all(postgres_engine)
