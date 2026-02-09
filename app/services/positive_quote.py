"""
Service functions for PositiveQuote model.
"""

from typing import List, Optional
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
        return PositiveQuoteRead(
            id=item.id,
            text=item.text,
            author=item.author,
            date=item.date,
        )


def get_positive_quote(item_id: int) -> Optional[PositiveQuoteRead]:
    with Session() as session:
        item = session.get(PositiveQuote, item_id)
        if not item:
            return None
        return PositiveQuoteRead(
            id=item.id,
            text=item.text,
            author=item.author,
        )


def list_positive_quotes() -> List[PositiveQuoteRead]:
    with Session() as session:
        items = session.query(PositiveQuote).all()
        return [
            PositiveQuoteRead(
                id=i.id,
                text=i.text,
                author=i.author,
            )
            for i in items
        ]
