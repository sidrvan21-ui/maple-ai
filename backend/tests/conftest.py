import pytest

from app.session import reset_store


@pytest.fixture(autouse=True)
def maple_tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("MAPLE_DB_PATH", str(tmp_path / "maple.db"))
    reset_store()
    yield
    reset_store()
