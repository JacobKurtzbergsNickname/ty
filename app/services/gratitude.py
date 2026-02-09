"""
Service functions for GratitudeItem model.
"""

from typing import List, Optional
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
        return GratitudeItemRead(
            id=item.id,
            title=item.title,
            description=item.description,
            how_happy_am_i_about_this=item.how_happy_am_i_about_this,
            reused=item.reused,
            date=item.date,
        )


def get_gratitude_item(item_id: int) -> Optional[GratitudeItemRead]:
    with Session() as session:
        item = session.get(GratitudeItem, item_id)
        if not item:
            return None
        return GratitudeItemRead(
            id=item.id,
            title=item.title,
            description=item.description,
            how_happy_am_i_about_this=item.how_happy_am_i_about_this,
            reused=item.reused,
        )


def list_gratitude_items() -> List[GratitudeItemRead]:
    with Session() as session:
        items = session.query(GratitudeItem).all()
        return [
            GratitudeItemRead(
                id=i.id,
                title=i.title,
                description=i.description,
                how_happy_am_i_about_this=i.how_happy_am_i_about_this,
                reused=i.reused,
            )
            for i in items
        ]
