"""
SQLAlchemy models for Gratitude app
"""

import datetime
from sqlalchemy import Column, Integer, String, Date
from app.database.base import Base


class GratitudeItem(Base):
    __tablename__ = "gratitude_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), default="")
    how_happy_am_i_about_this = Column(Integer, default=1)
    reused = Column(Integer, default=0)
    date = Column(Date, default=datetime.date.today, nullable=False, index=True)


class GoodThingsThatHappenedToMe(Base):
    __tablename__ = "good_things_that_happened_to_me"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(500), nullable=False)
    impact = Column(String(200), default="")
    date = Column(Date, default=datetime.date.today, nullable=False, index=True)


class Affirmation(Base):
    __tablename__ = "affirmations"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(300), nullable=False)
    author = Column(String(100), default="")
    date = Column(Date, default=datetime.date.today, nullable=False, index=True)


class PositiveQuote(Base):
    __tablename__ = "positive_quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(300), nullable=False)
    author = Column(String(100), default="")
    date = Column(Date, default=datetime.date.today, nullable=False, index=True)
