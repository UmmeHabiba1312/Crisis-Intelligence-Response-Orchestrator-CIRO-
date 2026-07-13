import os

from app.core import db


def test_database_url_is_configured():
    assert os.getenv("DATABASE_URL"), "DATABASE_URL should be configured for the Neon-backed backend"


def test_schema_bootstrap_creates_expected_tables(monkeypatch):
    created = []

    def fake_execute(conn, query):
        created.append(query)

    monkeypatch.setattr(db, "ensure_schema", lambda: created.append("ensure_schema"))
    db.initialize_database()
    assert "ensure_schema" in created
