"""
Service functions for PositiveQuote model.
"""

from sqlalchemy import select
from app.database.db import Session
from app.database.models import PositiveQuote
from app.validation.schemas import PositiveQuoteCreate, PositiveQuoteRead


def create_positive_quote(data: PositiveQuoteCreate) -> PositiveQuoteRead:
    with Session() as session:
        item = PositiveQuote(
            text=data.text,
            author=data.author,
            date=data.date,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return PositiveQuoteRead.model_validate(item)


def get_positive_quote(item_id: int) -> PositiveQuoteRead | None:
    with Session() as session:
        if item := session.get(PositiveQuote, item_id):
            return PositiveQuoteRead.model_validate(item)
        return None


def list_positive_quotes() -> list[PositiveQuoteRead]:
    with Session() as session:
        items = session.scalars(select(PositiveQuote)).all()
        return [PositiveQuoteRead.model_validate(i) for i in items]
