"""Tests for expense display functionality."""

from datetime import datetime

import pytest

from src.db import Expense
from src.expense_display import (
    format_amount,
    format_date,
    format_expenses_for_display,
    get_current_month,
    get_month_from_callback,
    get_month_name,
    get_previous_month,
    group_expenses_by_user,
)


@pytest.mark.fast
@pytest.mark.unit
def test_format_amount():
    """Test amount formatting."""
    assert format_amount(10.5) == "10.50 ₽"
    assert format_amount(0) == "0.00 ₽"
    assert format_amount(123.456) == "123.46 ₽"


@pytest.mark.fast
@pytest.mark.unit
def test_format_date():
    """Test date formatting."""
    # Valid ISO format
    assert format_date("2024-01-15T10:30:00+00:00") == "15.01"
    assert format_date("2024-12-31T23:59:59Z") == "31.12"

    # Invalid format should return original
    assert format_date("invalid-date") == "invalid-date"
    assert format_date("") == ""


@pytest.mark.fast
@pytest.mark.unit
def test_get_month_name():
    """Test month name retrieval."""
    assert get_month_name(1) == "январь"
    assert get_month_name(6) == "июнь"
    assert get_month_name(12) == "декабрь"
    assert get_month_name(13) == "месяц 13"  # Invalid month


@pytest.mark.fast
@pytest.mark.unit
def test_group_expenses_by_user():
    """Test grouping expenses by user."""
    expenses = [
        Expense(1, "Кофе", 100.0, "2024-01-01", 123),
        Expense(2, "Такси", 200.0, "2024-01-01", 123),
        Expense(3, "Обед", 300.0, "2024-01-01", 456),
    ]

    grouped = group_expenses_by_user(expenses)

    assert len(grouped) == 2
    assert len(grouped[123]) == 2
    assert len(grouped[456]) == 1
    assert grouped[123][0].description == "Кофе"
    assert grouped[456][0].description == "Обед"


@pytest.mark.fast
@pytest.mark.unit
def test_format_expenses_for_display_empty():
    """Test formatting empty expenses list."""
    result = format_expenses_for_display([], 2024, 1)
    assert "Расходов за январь 2024 не найдено" in result


@pytest.mark.fast
@pytest.mark.unit
def test_format_expenses_for_display_with_data():
    """Test formatting expenses with data."""
    expenses = [
        Expense(1, "Кофе", 100.0, "2024-01-15T10:00:00+00:00", 123),
        Expense(2, "Такси", 200.0, "2024-01-16T11:00:00+00:00", 123),
        Expense(3, "Обед", 300.0, "2024-01-17T12:00:00+00:00", 456),
    ]

    result = format_expenses_for_display(expenses, 2024, 1)

    assert "Расходы за январь 2024" in result
    assert "Пользователь 123" in result
    assert "Пользователь 456" in result
    assert "Кофе — 100.00 ₽" in result
    assert "Такси — 200.00 ₽" in result
    assert "Обед — 300.00 ₽" in result
    assert "Итого: 600.00 ₽" in result


@pytest.mark.fast
@pytest.mark.unit
def test_get_current_month():
    """Test getting current month."""
    year, month = get_current_month()
    now = datetime.now()
    assert year == now.year
    assert month == now.month


@pytest.mark.fast
@pytest.mark.unit
def test_get_previous_month():
    """Test getting previous month."""
    # January -> December of previous year
    assert get_previous_month(2024, 1) == (2023, 12)

    # February -> January of same year
    assert get_previous_month(2024, 2) == (2024, 1)

    # December -> November of same year
    assert get_previous_month(2024, 12) == (2024, 11)


@pytest.mark.fast
@pytest.mark.unit
def test_get_month_from_callback():
    """Test getting month from callback data."""
    current_year, current_month = get_current_month()

    # Test current month
    year, month = get_month_from_callback("month_current")
    assert year == current_year
    assert month == current_month

    # Test last month
    last_year, last_month = get_previous_month(current_year, current_month)
    year, month = get_month_from_callback("month_last")
    assert year == last_year
    assert month == last_month

    # Test previous month
    prev_year, prev_month = get_previous_month(last_year, last_month)
    year, month = get_month_from_callback("month_previous")
    assert year == prev_year
    assert month == prev_month

    # Test invalid callback
    year, month = get_month_from_callback("invalid")
    assert year == current_year
    assert month == current_month
