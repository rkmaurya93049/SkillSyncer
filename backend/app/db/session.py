import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _default_sqlite_url() -> str:
    configured_path = os.getenv("SKILLSYNCER_DB_PATH")
    if configured_path:
        db_path = Path(configured_path).expanduser()
    else:
        # Stable local default independent of the process working directory.
        db_path = Path(__file__).resolve().parents[1] / "evaluations.db"

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


DATABASE_URL = os.getenv("DATABASE_URL") or _default_sqlite_url()
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
