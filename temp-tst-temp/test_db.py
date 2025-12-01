import os
import sqlite3
import tempfile

import pytest

from src.db import init_db, insert_expense


@pytest.fixture()
def temp_db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_expenses.db")
        yield db_path


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.unit
def test_init_db_creates_table(temp_db_path):
    init_db(temp_db_path)
    conn = sqlite3.connect(temp_db_path)
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
        row = cur.fetchone()
        assert row is not None
        assert row[0] == "expenses"
    finally:
        conn.close()


@pytest.mark.fast
@pytest.mark.unit
def test_insert_and_read_back(temp_db_path):
    init_db(temp_db_path)
    new_id = insert_expense("Кофе", 10.5, user_id=123, db_path=temp_db_path)
    assert isinstance(new_id, int)

    conn = sqlite3.connect(temp_db_path)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM expenses WHERE id=?", (new_id,))
        row = cur.fetchone()
        assert row is not None
        assert row["description"] == "Кофе"
        assert row["amount"] == 10.5
        assert row["user_id"] == 123
        assert row["created_at"]
    finally:
        conn.close()


@pytest.mark.fast
@pytest.mark.unit
def test_insert_validations(temp_db_path):
    init_db(temp_db_path)
    with pytest.raises(ValueError):
        insert_expense("", 1, user_id=123, db_path=temp_db_path)
    with pytest.raises(ValueError):
        insert_expense("Кофе", 0, user_id=123, db_path=temp_db_path)
