"""Клавиатуры для Telegram бота."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from . import strings


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Создает главную клавиатуру с кнопкой просмотра расходов."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=strings.BUTTON_VIEW_EXPENSES, callback_data="view_expenses")]]
    )
    return keyboard


def get_month_selection_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру выбора месяца."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=strings.BUTTON_THIS_MONTH, callback_data="month_current")],
            [InlineKeyboardButton(text=strings.BUTTON_LAST_MONTH, callback_data="month_last")],
            [InlineKeyboardButton(text=strings.BUTTON_PREVIOUS_MONTH, callback_data="month_previous")],
            [InlineKeyboardButton(text=strings.BUTTON_BACK_TO_MENU, callback_data="back_to_menu")],
        ]
    )
    return keyboard


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой возврата в меню."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=strings.BUTTON_BACK_TO_MENU, callback_data="back_to_menu")]]
    )
    return keyboard
