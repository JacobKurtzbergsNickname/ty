"""
Service functions for Affirmation model.
"""

from typing import List, Optional
from app.database.db import Session
from app.database.models import Affirmation
from app.validation.schemas import AffirmationCreate, AffirmationRead


def create_affirmation(data: AffirmationCreate) -> AffirmationRead:
    with Session() as session:
        item = Affirmation(
            text=data.text,
            author=data.author,
            date=data.date,
        )
        session.add(item)
        session.commit()
        session.refresh(item)

        ar = AffirmationRead(
            id=int(item.id),
            text=item.text,
            author=item.author,
            date=item.date,
        )
        return ar


def get_affirmation(item_id: int) -> Optional[AffirmationRead]:
    with Session() as session:
        item = session.get(Affirmation, item_id)
        if not item:
            return None
        return AffirmationRead(
            id=int(item.id),
            text=item.text,
            author=item.author,
        )


def list_affirmations() -> List[AffirmationRead]:
    with Session() as session:
        items = session.query(Affirmation).all()
        return [
            AffirmationRead(
                id=i.id,
                text=i.text,
                author=i.author,
            )
            for i in items
        ]
