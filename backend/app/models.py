from datetime import datetime, timedelta, timezone
from email.policy import default
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, true
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///../data/sqlite/vocabulary.db"
class Base(DeclarativeBase):
    pass

class ConceptReview(Base):
    __tablename__ = "concept_reviews"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, index=True, nullable=False)
    context = Column(String, nullable=False)
    translation = Column(String, nullable=True)
    synonyms = Column(String, nullable=True) 

    # Spaced Repetition Logic (stages: 1, 2 , 3... corresponding to review intervals)
    review_stage = Column(Integer, default=1)
    next_review_date = Column(DateTime(timezone=true), default=lambda: datetime.now(timezone.utc) + timedelta(days=1))  # Next review in 1 day by default

    created_at = Column(DateTime(timezone=true), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=true), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))