from db.database import SessionLocal
from db.models import Highlight
from contextlib import contextmanager


@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_highlight(db, highlight_data):
    db_highlight = Highlight(**highlight_data)
    db.add(db_highlight)
    db.commit()
    db.refresh(db_highlight)
    return db_highlight
