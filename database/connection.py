"""
NexHR - Database Connection
Reads DATABASE_URL from .env. Falls back to a local SQLite file so the
project runs out-of-the-box with zero external setup. Swap DATABASE_URL
in .env to a PostgreSQL URI (e.g. postgresql+psycopg2://user:pass@host/db)
for a production deployment -- no other code needs to change.
"""
import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nexhr.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Return a new session. Caller is responsible for closing it."""
    return SessionLocal()


@contextmanager
def session_scope():
    """Context-managed session with automatic commit/rollback/close."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
