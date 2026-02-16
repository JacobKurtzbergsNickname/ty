"""
Database setup for FastHTML app (SQLite + SQLAlchemy 2.x)
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from .base import Base
from . import models  # pylint: disable=unused-import


def get_database_url() -> str:
    """Determine the correct SQLite DB URL based on environment."""

    # If set, use DATABASE_URL environment variable (allows overriding for testing/production)
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        return env_url

    # Development
    ty_env = os.environ.get("TY_ENV", "development").lower()
    if ty_env != "production":
        return get_dev_db_path()

    # Production
    return get_prod_db_path()


def ensure_db_file_exists(db_url: str) -> None:
    """Ensure the SQLite DB file exists (touch if missing)."""
    if not db_url.startswith("sqlite:///"):
        return

    db_path = db_url.replace("sqlite:///", "", 1)
    if os.path.exists(db_path):
        return

    with open(db_path, "ab"):
        print(f"Created new SQLite DB file at: {db_path}")


def get_dev_db_path() -> str:
    """Get the development SQLite DB path (used for testing)."""
    # Development: use <repo_root>/database/ty.sqlite3, where repo_root contains pyproject.toml
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            repo_root = parent
            break
    else:
        raise RuntimeError("Could not find project root from " + str(current))
    db_dir = repo_root / "app" / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "ty.sqlite3"
    return f"sqlite:///{db_path}"


def get_prod_db_path() -> str:
    # Production
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA environment variable not set on Windows.")
        db_dir = os.path.join(appdata, "ty")
    else:
        # Linux/Unix: prefer XDG_DATA_HOME when available, then fall back to
        # the freedesktop.org default (~/.local/share).
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            db_dir = os.path.join(xdg_data_home, "ty")
        else:
            home = os.environ.get("HOME")
            if home:
                db_dir = os.path.join(home, ".local", "share", "ty")
            else:
                # Last-resort Linux fallback for minimal/container environments.
                db_dir = "/var/lib/ty"
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "ty.sqlite3")
    return f"sqlite:///{db_path}"


DATABASE_URL = get_database_url()
ensure_db_file_exists(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=False, future=True)
Session = sessionmaker(engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Import all models and create all tables if they do not exist."""

    Base.metadata.create_all(engine)


init_db()
