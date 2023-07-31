from datetime import datetime

from stats.schemas import Event


def test_fix_ticker():
    event = Event(
        indicator="GDP",
        date=datetime.utcnow(),
        ticker="",
        title="Generate me: new ticker!",
        actual=1.0,
        country="US",
        currency="USD",
    )
    assert event.ticker == "USGMNT"


def test_fix_period():
    event = Event(
        indicator="GDP",
        date=datetime.utcnow(),
        ticker="AUCIG",
        title="RBA Trimmed Mean CPI YoY",
        actual=1.0,
        country="AU",
        currency="USD",
        period="Feb/2022",
    )
    assert event.period.value == "Feb"
