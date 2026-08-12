from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and guarantees
    the session is closed after the request, even on exceptions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
