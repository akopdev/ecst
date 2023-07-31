import pytest


@pytest.fixture()
def dsn():
    return "sqlite+aiosqlite:///:memory:"
