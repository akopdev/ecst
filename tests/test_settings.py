from datetime import datetime

import pytest

from stats.schemas import Settings

# Sample test cases for Settings schema
parse_date_data = [
    ("2020-01-01", datetime(2020, 1, 1, 0, 0)),
    ("2020-01-01 10:30:00", datetime(2020, 1, 1, 10, 30)),
]

parse_days_data = [
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


@pytest.mark.parametrize("date_str,expected", parse_date_data)
def test_parse_date(date_str, expected):
    for date_str, expected in parse_date_data:
        schema = Settings(storage="mongodb://localhost:27017", date_start=date_str)
        assert schema.date_start == expected




@pytest.mark.parametrize("days,inputs,expected", parse_days_data)
def test_parse_days(days, inputs, expected):
    for days, inputs, expected in parse_days_data:
        schema = Settings(storage="mongodb://localhost:27017", days=days, **inputs)
        assert schema.date_start == expected["date_start"]
        assert schema.date_end == expected["date_end"]
