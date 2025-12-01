"""Tests for new database functions."""

import os
import tempfile
from datetime import UTC, datetime

import pytest

from src.db import get_expenses_by_month, get_expenses_by_user_and_month, init_db, insert_expense


@pytest.fixture()
def temp_db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_expenses.db")
        yield db_path


@pytest.mark.fast
@pytest.mark.unit
def test_get_expenses_by_month_empty(temp_db_path):
    """Test getting expenses by month when no expenses exist."""
    init_db(temp_db_path)
    expenses = get_expenses_by_month(2024, 1, temp_db_path)
    assert expenses == []


@pytest.mark.fast
@pytest.mark.unit
def test_get_expenses_by_month_with_data(temp_db_path):
    """Test getting expenses by month with data."""
    init_db(temp_db_path)

    # Insert test expenses
    insert_expense("Кофе", 100.0, user_id=123, db_path=temp_db_path)
    insert_expense("Такси", 200.0, user_id=456, db_path=temp_db_path)

    # Get expenses for current month
    current_year, current_month = datetime.now(UTC).year, datetime.now(UTC).month
    expenses = get_expenses_by_month(current_year, current_month, temp_db_path)

    assert len(expenses) == 2
    assert expenses[0].description == "Кофе"
    assert expenses[0].amount == 100.0
    assert expenses[0].user_id == 123
    assert expenses[1].description == "Такси"
    assert expenses[1].amount == 200.0
    assert expenses[1].user_id == 456


@pytest.mark.fast
@pytest.mark.unit
def test_get_expenses_by_user_and_month_empty(temp_db_path):
    """Test getting expenses by user and month when no expenses exist."""
    init_db(temp_db_path)
    expenses = get_expenses_by_user_and_month(123, 2024, 1, temp_db_path)
    assert expenses == []


@pytest.mark.fast
@pytest.mark.unit
def test_get_expenses_by_user_and_month_with_data(temp_db_path):
    """Test getting expenses by user and month with data."""
    init_db(temp_db_path)

    # Insert test expenses
    insert_expense("Кофе", 100.0, user_id=123, db_path=temp_db_path)
    insert_expense("Такси", 200.0, user_id=123, db_path=temp_db_path)
    insert_expense("Обед", 300.0, user_id=456, db_path=temp_db_path)

    # Get expenses for user 123
    current_year, current_month = datetime.now(UTC).year, datetime.now(UTC).month
    expenses = get_expenses_by_user_and_month(123, current_year, current_month, temp_db_path)

    assert len(expenses) == 2
    assert expenses[0].description == "Кофе"
    assert expenses[0].amount == 100.0
    assert expenses[0].user_id == 123
    assert expenses[1].description == "Такси"
    assert expenses[1].amount == 200.0
    assert expenses[1].user_id == 123


@pytest.mark.fast
@pytest.mark.unit
def test_get_expenses_by_user_and_month_wrong_user(temp_db_path):
    """Test getting expenses by user and month for wrong user."""
    init_db(temp_db_path)

    # Insert test expense for user 123
    insert_expense("Кофе", 100.0, user_id=123, db_path=temp_db_path)

    # Try to get expenses for user 456
    current_year, current_month = datetime.now(UTC).year, datetime.now(UTC).month
    expenses = get_expenses_by_user_and_month(456, current_year, current_month, temp_db_path)

    assert expenses == []


@pytest.mark.fast
@pytest.mark.unit
def test_get_expenses_by_month_wrong_month(temp_db_path):
    """Test getting expenses by month for wrong month."""
    init_db(temp_db_path)

    # Insert test expense
    insert_expense("Кофе", 100.0, user_id=123, db_path=temp_db_path)

    # Try to get expenses for different month
    expenses = get_expenses_by_month(2023, 12, temp_db_path)

    assert expenses == []
