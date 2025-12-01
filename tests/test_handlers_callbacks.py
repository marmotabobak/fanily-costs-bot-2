"""Tests for callback handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Message, User

from src.handlers import handle_back_to_menu_callback, handle_month_selection_callback, handle_view_expenses_callback


@pytest.fixture
def mock_callback():
    """Create a mock CallbackQuery."""
    user = MagicMock(spec=User)
    user.id = 123456789

    callback = MagicMock(spec=CallbackQuery)
    callback.data = "view_expenses"
    callback.from_user = user
    callback.answer = AsyncMock()

    message = MagicMock(spec=Message)
    message.edit_text = AsyncMock()
    callback.message = message

    return callback


@pytest.fixture
def mock_month_callback():
    """Create a mock CallbackQuery for month selection."""
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
async def test_handle_view_expenses_callback_success(mock_callback):
    """Test successful view expenses callback."""
    with patch("src.handlers.auth.is_user_allowed", return_value=True):
        await handle_view_expenses_callback(mock_callback)

        # Check that message was edited with month selection
        mock_callback.message.edit_text.assert_called_once()
        call_args = mock_callback.message.edit_text.call_args
        assert "Выберите месяц для просмотра расходов" in call_args[0][0]

        # Check that callback was answered
        mock_callback.answer.assert_called_once()


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_view_expenses_callback_access_denied(mock_callback):
    """Test view expenses callback with access denied."""
    with patch("src.handlers.auth.is_user_allowed", return_value=False):
        await handle_view_expenses_callback(mock_callback)

        # Check that access denied message was sent
        mock_callback.answer.assert_called_once_with("⛔ У вас нет доступа к этому боту.")

        # Check that message was not edited
        mock_callback.message.edit_text.assert_not_called()


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_month_selection_callback_success(mock_month_callback):
    """Test successful month selection callback."""
    # Mock expenses data
    mock_expenses = [
        MagicMock(description="Кофе", amount=100.0, created_at="2024-01-15T10:00:00+00:00", user_id=123456789),
        MagicMock(description="Такси", amount=200.0, created_at="2024-01-16T11:00:00+00:00", user_id=123456789),
    ]

    with (
        patch("src.handlers.auth.is_user_allowed", return_value=True),
        patch("src.handlers.db.get_expenses_by_month", return_value=mock_expenses),
    ):

        await handle_month_selection_callback(mock_month_callback)

        # Check that message was edited with expenses
        mock_month_callback.message.edit_text.assert_called_once()
        call_args = mock_month_callback.message.edit_text.call_args
        expenses_text = call_args[0][0]

        # Check that expenses are displayed correctly
        assert "Расходы за" in expenses_text
        assert "Кофе — 100.00 ₽" in expenses_text
        assert "Такси — 200.00 ₽" in expenses_text
        assert "Итого:" in expenses_text

        # Check that callback was answered
        mock_month_callback.answer.assert_called_once()


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_month_selection_callback_empty_expenses(mock_month_callback):
    """Test month selection callback with no expenses."""
    with (
        patch("src.handlers.auth.is_user_allowed", return_value=True),
        patch("src.handlers.db.get_expenses_by_month", return_value=[]),
    ):

        await handle_month_selection_callback(mock_month_callback)

        # Check that message was edited with empty message
        mock_month_callback.message.edit_text.assert_called_once()
        call_args = mock_month_callback.message.edit_text.call_args
        expenses_text = call_args[0][0]

        # Check that empty message is displayed
        assert "Расходов за" in expenses_text
        assert "не найдено" in expenses_text

        # Check that callback was answered
        mock_month_callback.answer.assert_called_once()


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_month_selection_callback_error(mock_month_callback):
    """Test month selection callback with error."""
    with (
        patch("src.handlers.auth.is_user_allowed", return_value=True),
        patch("src.handlers.db.get_expenses_by_month", side_effect=Exception("Database error")),
    ):

        await handle_month_selection_callback(mock_month_callback)

        # Check that error message was sent
        mock_month_callback.answer.assert_called_once_with("❌ Ошибка при получении расходов.")

        # Check that error message was edited
        mock_month_callback.message.edit_text.assert_called_once()
        call_args = mock_month_callback.message.edit_text.call_args
        assert "Произошла ошибка при получении расходов" in call_args[0][0]


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_back_to_menu_callback_success(mock_callback):
    """Test successful back to menu callback."""
    with patch("src.handlers.auth.is_user_allowed", return_value=True):
        await handle_back_to_menu_callback(mock_callback)

        # Check that message was edited with help text
        mock_callback.message.edit_text.assert_called_once()
        call_args = mock_callback.message.edit_text.call_args
        assert "Привет! Я бот для учёта расходов" in call_args[0][0]

        # Check that callback was answered
        mock_callback.answer.assert_called_once()


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_back_to_menu_callback_access_denied(mock_callback):
    """Test back to menu callback with access denied."""
    with patch("src.handlers.auth.is_user_allowed", return_value=False):
        await handle_back_to_menu_callback(mock_callback)

        # Check that access denied message was sent
        mock_callback.answer.assert_called_once_with("⛔ У вас нет доступа к этому боту.")

        # Check that message was not edited
        mock_callback.message.edit_text.assert_not_called()
