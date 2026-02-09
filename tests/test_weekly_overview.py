from datetime import date, timedelta
from app.services.weekly_overview import get_tracked_objects_by_week


def test_get_tracked_objects_by_week_empty():
    # Use a week far in the past/future to ensure empty DB
    start = date(1999, 1, 4)
    end = start + timedelta(days=6)
    data = get_tracked_objects_by_week(start, end)
    assert isinstance(data, dict)
    assert set(data.keys()) == {"gratitude", "good_things", "affirmations", "quotes"}
    for v in data.values():
        assert isinstance(v, list)
        assert len(v) == 0 or all(hasattr(item, "id") for item in v)


def test_get_tracked_objects_by_week_types():
    # Just check that the function returns lists of the right type keys
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    data = get_tracked_objects_by_week(start, end)
    assert set(data.keys()) == {"gratitude", "good_things", "affirmations", "quotes"}
    for v in data.values():
        assert isinstance(v, list)
