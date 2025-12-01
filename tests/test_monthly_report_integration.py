"""Integration tests for monthly report functionality."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Message, User

from src.db import Expense
from src.handlers import handle_month_selection_callback


@pytest.fixture
def mock_callback_with_user():
    """Create a mock CallbackQuery with specific user."""
    user = MagicMock(spec=User)
    user.id = 123456789

    callback = MagicMock(spec=CallbackQuery)
    callback.data = "month_current"
    callback.from_user = user
    callback.answer = AsyncMock()

    message = MagicMock(spec=Message)
    message.edit_text = AsyncMock()
    callback.message = message

    return callback


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_monthly_report_with_multiple_users(mock_callback_with_user):
    """Test monthly report with multiple users and detailed formatting."""
    # Create realistic test data
    current_year = datetime.now(UTC).year
    current_month = datetime.now(UTC).month

    mock_expenses = [
        Expense(
            id=1,
            description="Кофе в кафе",
            amount=150.50,
            created_at=f"{current_year}-{current_month:02d}-15T10:30:00+00:00",
            user_id=123456789,
        ),
        Expense(
            id=2,
            description="Такси до дома",
            amount=250.0,
            created_at=f"{current_year}-{current_month:02d}-15T18:45:00+00:00",
            user_id=123456789,
        ),
        Expense(
            id=3,
            description="Обед в ресторане",
            amount=1200.75,
            created_at=f"{current_year}-{current_month:02d}-16T13:20:00+00:00",
            user_id=987654321,
        ),
        Expense(
            id=4,
            description="Продукты в магазине",
            amount=850.25,
            created_at=f"{current_year}-{current_month:02d}-17T09:15:00+00:00",
            user_id=123456789,
        ),
    ]

    with (
        patch("src.handlers.auth.is_user_allowed", return_value=True),
        patch("src.handlers.db.get_expenses_by_month", return_value=mock_expenses),
    ):

        await handle_month_selection_callback(mock_callback_with_user)

        # Check that message was edited
        mock_callback_with_user.message.edit_text.assert_called_once()
        call_args = mock_callback_with_user.message.edit_text.call_args
        report_text = call_args[0][0]

        # Verify the report structure
        assert "📊 Расходы за" in report_text
        assert f"{current_year}" in report_text

        # Check user sections
        assert "👤 Пользователь 123456789:" in report_text
        assert "👤 Пользователь 987654321:" in report_text

        # Check individual expenses
        assert "• Кофе в кафе — 150.50 ₽" in report_text
        assert "• Такси до дома — 250.00 ₽" in report_text
        assert "• Обед в ресторане — 1200.75 ₽" in report_text
        assert "• Продукты в магазине — 850.25 ₽" in report_text

        # Check user totals
        assert "💰 Итого: 1250.75 ₽" in report_text  # 150.50 + 250.0 + 850.25
        assert "💰 Итого: 1200.75 ₽" in report_text  # 1200.75

        # Check grand total
        assert "💰 Итого: 2451.50 ₽" in report_text  # 1250.75 + 1200.75

        # Check that callback was answered
        mock_callback_with_user.answer.assert_called_once()


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_monthly_report_empty_month(mock_callback_with_user):
    """Test monthly report with no expenses."""
    with (
        patch("src.handlers.auth.is_user_allowed", return_value=True),
        patch("src.handlers.db.get_expenses_by_month", return_value=[]),
    ):

        await handle_month_selection_callback(mock_callback_with_user)

        # Check that message was edited
        mock_callback_with_user.message.edit_text.assert_called_once()
        call_args = mock_callback_with_user.message.edit_text.call_args
        report_text = call_args[0][0]

        # Verify empty message
        assert "📭 Расходов за" in report_text
        assert "не найдено" in report_text

        # Check that callback was answered
        mock_callback_with_user.answer.assert_called_once()


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_monthly_report_single_user(mock_callback_with_user):
    """Test monthly report with single user."""
    current_year = datetime.now(UTC).year
    current_month = datetime.now(UTC).month

    mock_expenses = [
        Expense(
            id=1,
            description="Завтрак",
            amount=300.0,
            created_at=f"{current_year}-{current_month:02d}-01T08:00:00+00:00",
            user_id=123456789,
        ),
        Expense(
            id=2,
            description="Обед",
            amount=500.0,
            created_at=f"{current_year}-{current_month:02d}-01T13:00:00+00:00",
            user_id=123456789,
        ),
    ]

    with (
        patch("src.handlers.auth.is_user_allowed", return_value=True),
        patch("src.handlers.db.get_expenses_by_month", return_value=mock_expenses),
    ):

        await handle_month_selection_callback(mock_callback_with_user)

        # Check that message was edited
        mock_callback_with_user.message.edit_text.assert_called_once()
        call_args = mock_callback_with_user.message.edit_text.call_args
        report_text = call_args[0][0]

        # Verify the report structure
        assert "📊 Расходы за" in report_text
        assert "👤 Пользователь 123456789:" in report_text
        assert "• Завтрак — 300.00 ₽" in report_text
        assert "• Обед — 500.00 ₽" in report_text
        assert "💰 Итого: 800.00 ₽" in report_text  # User total
        assert "💰 Итого: 800.00 ₽" in report_text  # Grand total (same as user total)

        # Check that callback was answered
        mock_callback_with_user.answer.assert_called_once()


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_monthly_report_different_months(mock_callback_with_user):
    """Test monthly report for different months."""
    # Test for last month
    mock_callback_with_user.data = "month_last"

    # Mock expenses for last month
    last_month = datetime.now(UTC).month - 1 if datetime.now(UTC).month > 1 else 12
    last_year = datetime.now(UTC).year if datetime.now(UTC).month > 1 else datetime.now(UTC).year - 1

    mock_expenses = [
        Expense(
            id=1,
            description="Новогодний ужин",
            amount=5000.0,
            created_at=f"{last_year}-{last_month:02d}-31T20:00:00+00:00",
            user_id=123456789,
        )
    ]

    with (
        patch("src.handlers.auth.is_user_allowed", return_value=True),
        patch("src.handlers.db.get_expenses_by_month", return_value=mock_expenses),
    ):

        await handle_month_selection_callback(mock_callback_with_user)

        # Check that message was edited
        mock_callback_with_user.message.edit_text.assert_called_once()
        call_args = mock_callback_with_user.message.edit_text.call_args
        report_text = call_args[0][0]

        # Verify the report structure
        assert "📊 Расходы за" in report_text
        assert f"{last_year}" in report_text
        assert "• Новогодний ужин — 5000.00 ₽" in report_text
        assert "💰 Итого: 5000.00 ₽" in report_text

        # Check that callback was answered
        mock_callback_with_user.answer.assert_called_once()
