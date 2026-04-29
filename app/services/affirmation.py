"""
Service functions for Affirmation model.
"""

from sqlalchemy import select
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
        return AffirmationRead.model_validate(item)


def get_affirmation(item_id: int) -> AffirmationRead | None:
    with Session() as session:
        if item := session.get(Affirmation, item_id):
            return AffirmationRead.model_validate(item)
        return None


def list_affirmations() -> list[AffirmationRead]:
    with Session() as session:
        items = session.scalars(select(Affirmation)).all()
        return [AffirmationRead.model_validate(i) for i in items]
