from datetime import datetime

import pytest

from app.schemas import Settings

test_dates = [
    ("2020-01-01", datetime(2020, 1, 1, 0, 0)),
    ("2020-01-01 10:30:00", datetime(2020, 1, 1, 10, 30)),
]


@pytest.mark.parametrize("date_str, expected", test_dates)
def test_parse_date(date_str, expected):
    for date_str, expected in test_dates:
        schema = Settings(storage="mongodb://localhost:27017", date_start=date_str)
        assert schema.date_start == expected


test_days = [
    (
        1,
        {"date_start": datetime(2020, 1, 1, 0, 0)},
        {"date_start": datetime(2020, 1, 1, 0, 0), "date_end": datetime(2020, 1, 2, 0, 0)},
    ),
    (
        -1,
        {"date_start": datetime(2020, 1, 1, 0, 0)},
        {"date_start": datetime(2020, 1, 1, 0, 0), "date_end": datetime(2019, 12, 31, 0, 0)},
    ),
    (
        1,
        {"date_end": datetime(2020, 1, 2, 0, 0)},
        {"date_start": datetime(2020, 1, 1, 0, 0), "date_end": datetime(2020, 1, 2, 0, 0)},
    ),
    (
        -1,
        {"date_end": datetime(2020, 1, 2, 0, 0)},
        {"date_start": datetime(2020, 1, 1, 0, 0), "date_end": datetime(2020, 1, 2, 0, 0)},
    ),
    (
        None,
        {"date_start": datetime(2020, 1, 1, 0, 0), "date_end": datetime(2020, 1, 2, 0, 0)},
        {"date_start": datetime(2020, 1, 1, 0, 0), "date_end": datetime(2020, 1, 2, 0, 0)},
    ),
]


@pytest.mark.parametrize("days,inputs,expected", test_days)
def test_parse_days(days, inputs, expected):
    for days, inputs, expected in test_days:
        schema = Settings(storage="mongodb://localhost:27017", days=days, **inputs)
        assert schema.date_start == expected["date_start"]
        assert schema.date_end == expected["date_end"]
