"""
Service functions for GoodThingsThatHappenedToMe model.
"""

from sqlalchemy import select
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
        return GoodThingsThatHappenedToMeRead.model_validate(item)


def get_good_thing(item_id: int) -> GoodThingsThatHappenedToMeRead | None:
    with Session() as session:
        if item := session.get(GoodThingsThatHappenedToMe, item_id):
            return GoodThingsThatHappenedToMeRead.model_validate(item)
        return None


def list_good_things() -> list[GoodThingsThatHappenedToMeRead]:
    with Session() as session:
        items = session.scalars(select(GoodThingsThatHappenedToMe)).all()
        return [GoodThingsThatHappenedToMeRead.model_validate(i) for i in items]
