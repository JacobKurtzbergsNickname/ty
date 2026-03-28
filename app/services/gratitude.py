"""
Service functions for GratitudeItem model.
"""

from sqlalchemy import select
from app.database.db import Session
from app.database.models import GratitudeItem
from app.validation.schemas import GratitudeItemCreate, GratitudeItemRead


def create_gratitude_item(data: GratitudeItemCreate) -> GratitudeItemRead:
    with Session() as session:
        item = GratitudeItem(
            title=data.title,
            description=data.description,
            how_happy_am_i_about_this=data.how_happy_am_i_about_this,
            reused=data.reused,
            date=data.date,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return GratitudeItemRead.model_validate(item)


def get_gratitude_item(item_id: int) -> GratitudeItemRead | None:
    with Session() as session:
        if item := session.get(GratitudeItem, item_id):
            return GratitudeItemRead.model_validate(item)
        return None


def list_gratitude_items() -> list[GratitudeItemRead]:
    with Session() as session:
        items = session.scalars(select(GratitudeItem)).all()
        return [GratitudeItemRead.model_validate(i) for i in items]
