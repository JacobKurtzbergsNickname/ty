import calendar
from datetime import date, timedelta
from typing import Sequence, TypeVar
from fasthtml.common import *
from fasthtml.core import Request, FT
from app.validation.schemas import (
    GratitudeItemRead,
    GoodThingsThatHappenedToMeRead,
    AffirmationRead,
    PositiveQuoteRead,
)
from app.services.weekly_overview import get_tracked_objects_by_week

weekly_overview_app, rt = fast_app()

T = TypeVar("T")


def get_week_range(ref_date: date) -> tuple[date, date]:
    """Return (monday, sunday) for the week containing ref_date."""
    monday = ref_date - timedelta(days=ref_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


@rt("/", name="weekly_overview")
def weekly_overview_view(req: Request) -> FT:
    """Weekly overview page for gratitude, good things, affirmations, and quotes."""
    today = date.today()
    date_str = req.query_params.get("date", today.isoformat())
    try:
        ref_date = date.fromisoformat(date_str)
    except ValueError:
        ref_date = today
    week_start, week_end = get_week_range(ref_date)
    data = get_tracked_objects_by_week(week_start, week_end)

    prev_week = (week_start - timedelta(days=7)).isoformat()
    next_week = (week_start + timedelta(days=7)).isoformat()

    nav = Nav(
        A("← Previous", href=f"/weekly-overview?date={prev_week}", cls="secondary"),
        Span(f"{week_start} to {week_end}", cls="nav-label"),
        A("Next →", href=f"/weekly-overview?date={next_week}", cls="secondary"),
        cls="container mb-4 flex space-between align-center",
    )

    # Helper to get day names for the week (robust, no range(7))
    day_names = []
    current = week_start
    while current <= week_end:
        day_names.append((current, calendar.day_name[current.weekday()]))
        current += timedelta(days=1)

    # Helper to group all objects by day
    def group_by_day(items: Sequence[T]) -> dict[date, list[T]]:
        result = {d[0]: [] for d in day_names}
        for item in items:
            item_date = getattr(item, "date", None) or getattr(item, "day", None)
            if item_date and item_date in result:
                result[item_date].append(item)
            else:
                result[day_names[0][0]].append(item)
        return result

    gratitude_by_day = group_by_day(data["gratitude"])
    good_by_day = group_by_day(data["good_things"])
    affirm_by_day = group_by_day(data["affirmations"])
    quotes_by_day = group_by_day(data["quotes"])

    def render_day(d: date, dname: str) -> FT:
        sections = []
        if gratitude_by_day[d]:
            sections.append(
                Div(
                    H4("Gratitude Items", cls="mb-1"),
                    *[
                        Div(render_gratitude(item), cls="mb-2")
                        for item in gratitude_by_day[d]
                    ],
                    cls="mb-3",
                )
            )
        if good_by_day[d]:
            sections.append(
                Div(
                    H4("Good Things That Happened", cls="mb-1"),
                    *[
                        Div(render_good_thing(item), cls="mb-2")
                        for item in good_by_day[d]
                    ],
                    cls="mb-3",
                )
            )
        if affirm_by_day[d]:
            sections.append(
                Div(
                    H4("Affirmations", cls="mb-1"),
                    *[
                        Div(render_affirmation(item), cls="mb-2")
                        for item in affirm_by_day[d]
                    ],
                    cls="mb-3",
                )
            )
        if quotes_by_day[d]:
            sections.append(
                Div(
                    H4("Positive Quotes", cls="mb-1"),
                    *[Div(render_quote(item), cls="mb-2") for item in quotes_by_day[d]],
                    cls="mb-3",
                )
            )
        if not sections:
            sections.append(
                Div(
                    "Nothing to show, but I am grateful for you!",
                    cls="empty-section mb-3",
                )
            )
        return Section(H3(dname, cls="mb-2"), *sections, cls="card p-4 mb-4")

    def render_gratitude(item: GratitudeItemRead) -> FT:
        return Div(
            H3(item.title),
            P(item.description),
            P(f"Happiness: {item.how_happy_am_i_about_this}"),
            P(f"Reused: {item.reused}"),
            cls="gratitude-item",
        )

    def render_good_thing(item: GoodThingsThatHappenedToMeRead) -> FT:
        return Div(
            P(item.description), P(f"Impact: {item.impact}"), cls="good-thing-item"
        )

    def render_affirmation(item: AffirmationRead) -> FT:
        return Div(P(item.text), P(f"Author: {item.author}"), cls="affirmation-item")

    def render_quote(item: PositiveQuoteRead) -> FT:
        return Div(P(item.text), P(f"Author: {item.author}"), cls="quote-item")

    return Titled(
        f"Weekly Overview: {week_start} to {week_end}",
        nav,
        Div(*[render_day(d, dname) for d, dname in day_names], cls="container"),
        head=[
            Link(
                rel="stylesheet",
                href="https://unpkg.com/@picocss/pico@latest/css/pico.min.css",
            )
        ],
        cls="weekly-overview bg-dark text-light min-vh-100",
    )
