"""
Pydantic schemas for validation (example: ToDo item)
"""

from datetime import date as D
from pydantic import BaseModel, Field


class GratitudeItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    how_happy_am_i_about_this: int = Field(1, ge=1)
    reused: int = Field(0, ge=0)
    date: D = Field(default_factory=D.today)


class GratitudeItemRead(BaseModel):
    id: int
    title: str
    description: str
    how_happy_am_i_about_this: int
    reused: int
    date: D = Field(default_factory=D.today)


class GoodThingsThatHappenedToMeCreate(BaseModel):
    description: str = Field(..., max_length=500)
    impact: str = Field("", max_length=200)
    date: D = Field(default_factory=D.today)


class GoodThingsThatHappenedToMeRead(BaseModel):
    id: int
    description: str
    impact: str
    date: D = Field(default_factory=D.today)


class AffirmationCreate(BaseModel):
    text: str = Field(..., max_length=300)
    author: str = Field("", max_length=100)
    date: D = Field(default_factory=D.today)


class AffirmationRead(BaseModel):
    id: int
    text: str
    author: str
    date: D = Field(default_factory=D.today)


class PositiveQuoteCreate(BaseModel):
    text: str = Field(..., max_length=300)
    author: str = Field("", max_length=100)
    date: D = Field(default_factory=D.today)


class PositiveQuoteRead(BaseModel):
    id: int
    text: str
    author: str
    date: D = Field(default_factory=D.today)
