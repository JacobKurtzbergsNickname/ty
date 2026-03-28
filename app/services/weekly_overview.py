"""
Service function to aggregate all tracked objects by week.
"""

from datetime import date
from typing import Any
from sqlalchemy import select
from app.database.db import Session
from app.database.models import (
    GratitudeItem,
    GoodThingsThatHappenedToMe,
    Affirmation,
    PositiveQuote,
)
from app.validation.schemas import (
    GratitudeItemRead,
    GoodThingsThatHappenedToMeRead,
    AffirmationRead,
    PositiveQuoteRead,
)


def get_tracked_objects_by_week(
    start_date: date, end_date: date
) -> dict[str, list[Any]]:
    """
    Returns a dict with keys: 'gratitude', 'good_things', 'affirmations', 'quotes',
    each containing a list of items created between start_date and end_date (inclusive).
    """
    with Session() as session:
        # Try to filter by created_at if present, else fallback to all
        def filter_by_date(model, schema):
            # Only filter if model has created_at
            if hasattr(model, "created_at"):
                q = select(model).where(
                    model.created_at >= start_date,
                    model.created_at <= end_date,
                )
                items = session.scalars(q).all()
            else:
                items = session.scalars(select(model)).all()
            return [schema.model_validate(item) for item in items]

        result = {
            "gratitude": filter_by_date(GratitudeItem, GratitudeItemRead),
            "good_things": filter_by_date(
                GoodThingsThatHappenedToMe, GoodThingsThatHappenedToMeRead
            ),
            "affirmations": filter_by_date(Affirmation, AffirmationRead),
            "quotes": filter_by_date(PositiveQuote, PositiveQuoteRead),
        }
        return result
