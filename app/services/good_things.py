"""
Service functions for GoodThingsThatHappenedToMe model.
"""

from typing import List, Optional
from app.database.db import Session
from app.database.models import GoodThingsThatHappenedToMe
from app.validation.schemas import (
    GoodThingsThatHappenedToMeCreate,
    GoodThingsThatHappenedToMeRead,
)


def create_good_thing(
    data: GoodThingsThatHappenedToMeCreate,
) -> GoodThingsThatHappenedToMeRead:
    with Session() as session:
        item = GoodThingsThatHappenedToMe(
            description=data.description,
            impact=data.impact,
            date=data.date,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return GoodThingsThatHappenedToMeRead(
            id=item.id,
            description=item.description,
            impact=item.impact,
            date=item.date,
        )


def get_good_thing(item_id: int) -> Optional[GoodThingsThatHappenedToMeRead]:
    with Session() as session:
        item = session.get(GoodThingsThatHappenedToMe, item_id)
        if not item:
            return None
        return GoodThingsThatHappenedToMeRead(
            id=item.id,
            description=item.description,
            impact=item.impact,
        )


def list_good_things() -> List[GoodThingsThatHappenedToMeRead]:
    with Session() as session:
        items = session.query(GoodThingsThatHappenedToMe).all()
        return [
            GoodThingsThatHappenedToMeRead(
                id=i.id,
                description=i.description,
                impact=i.impact,
            )
            for i in items
        ]
