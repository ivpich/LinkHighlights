from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Highlight(Base):
    __tablename__ = 'link_highlights'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    date = Column(String, nullable=False)
    text = Column(Text)
    highlights_json = Column(JSON, nullable=False)
    embedding_tokens = Column(Integer, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    origin_duration_seconds = Column(Integer, nullable=True)
    origin_duration = Column(String, nullable=False)
    highlight_duration_seconds = Column(Integer, nullable=True)
    highlight_duration = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Comment(comment_id='{self.comment_id}', post_id='{self.post_id}')>"
