"""Tests for keyboard functionality."""

import pytest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.keyboards import get_back_to_menu_keyboard, get_main_keyboard, get_month_selection_keyboard


@pytest.mark.fast
@pytest.mark.unit
def test_get_main_keyboard():
    """Test main keyboard creation."""
    keyboard = get_main_keyboard()

    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 1

    button = keyboard.inline_keyboard[0][0]
    assert isinstance(button, InlineKeyboardButton)
    assert button.text == "📊 Показать расходы"
    assert button.callback_data == "view_expenses"


@pytest.mark.fast
@pytest.mark.unit
def test_get_month_selection_keyboard():
    """Test month selection keyboard creation."""
    keyboard = get_month_selection_keyboard()

    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 4  # 4 rows

    # Check first row (current month)
    assert len(keyboard.inline_keyboard[0]) == 1
    assert keyboard.inline_keyboard[0][0].text == "📅 Этот месяц"
    assert keyboard.inline_keyboard[0][0].callback_data == "month_current"

    # Check second row (last month)
    assert len(keyboard.inline_keyboard[1]) == 1
    assert keyboard.inline_keyboard[1][0].text == "📅 Прошлый месяц"
    assert keyboard.inline_keyboard[1][0].callback_data == "month_last"

    # Check third row (previous month)
    assert len(keyboard.inline_keyboard[2]) == 1
    assert keyboard.inline_keyboard[2][0].text == "📅 Предыдущий месяц"
    assert keyboard.inline_keyboard[2][0].callback_data == "month_previous"

    # Check fourth row (back to menu)
    assert len(keyboard.inline_keyboard[3]) == 1
    assert keyboard.inline_keyboard[3][0].text == "🔙 Назад в меню"
    assert keyboard.inline_keyboard[3][0].callback_data == "back_to_menu"


@pytest.mark.fast
@pytest.mark.unit
def test_get_back_to_menu_keyboard():
    """Test back to menu keyboard creation."""
    keyboard = get_back_to_menu_keyboard()

    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 1

    button = keyboard.inline_keyboard[0][0]
    assert isinstance(button, InlineKeyboardButton)
    assert button.text == "🔙 Назад в меню"
    assert button.callback_data == "back_to_menu"
