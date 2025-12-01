"""Модуль для отображения расходов."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from . import strings
from .db import Expense


def format_amount(amount: float) -> str:
    """Форматирует сумму для отображения."""
    return f"{amount:.2f} ₽"


def format_date(date_str: str) -> str:
    """Форматирует дату для отображения."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d.%m")
    except (ValueError, AttributeError):
        return date_str


def get_month_name(month: int) -> str:
    """Возвращает название месяца."""
    if 1 <= month <= 12:
        return strings.MONTH_NAMES[month - 1]
    return f"месяц {month}"


def group_expenses_by_user(expenses: List[Expense]) -> Dict[int, List[Expense]]:
    """Группирует расходы по пользователям."""
    grouped = defaultdict(list)
    for expense in expenses:
        grouped[expense.user_id].append(expense)
    return dict(grouped)


def format_expenses_for_display(expenses: List[Expense], year: int, month: int, show_by_user: bool = True) -> str:
    """Форматирует расходы для отображения."""
    if not expenses:
        month_name = get_month_name(month)
        return strings.EXPENSES_EMPTY_TEMPLATE.format(month_name=month_name, year=year)

    month_name = get_month_name(month)
    result = strings.EXPENSES_HEADER_TEMPLATE.format(month_name=month_name, year=year)

    if show_by_user:
        # Группируем по пользователям
        grouped_expenses = group_expenses_by_user(expenses)
        total_amount = 0.0

        for user_id, user_expenses in grouped_expenses.items():
            user_name = f"Пользователь {user_id}"
            result += strings.EXPENSES_USER_HEADER_TEMPLATE.format(user_name=user_name)

            user_total = 0.0
            for expense in user_expenses:
                amount_str = format_amount(expense.amount)
                date_str = format_date(expense.created_at)
                result += strings.EXPENSES_ITEM_TEMPLATE.format(
                    description=expense.description, amount_str=amount_str, date=date_str
                )
                user_total += expense.amount
                total_amount += expense.amount

            result += f"  💰 Итого: {format_amount(user_total)}\n\n"

        result += strings.EXPENSES_TOTAL_TEMPLATE.format(total_amount_str=format_amount(total_amount))
    else:
        # Показываем все расходы в одном списке
        total_amount = 0.0
        for expense in expenses:
            amount_str = format_amount(expense.amount)
            date_str = format_date(expense.created_at)
            result += strings.EXPENSES_ITEM_TEMPLATE.format(
                description=expense.description, amount_str=amount_str, date=date_str
            )
            total_amount += expense.amount

        result += strings.EXPENSES_TOTAL_TEMPLATE.format(total_amount_str=format_amount(total_amount))

    return result


def get_current_month() -> tuple[int, int]:
    """Возвращает текущий год и месяц."""
    now = datetime.now()
    return now.year, now.month


def get_previous_month(year: int, month: int) -> tuple[int, int]:
    """Возвращает предыдущий месяц."""
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1


def get_month_from_callback(callback_data: str) -> tuple[int, int]:
    """Определяет месяц из callback_data."""
    current_year, current_month = get_current_month()

    if callback_data == "month_current":
        return current_year, current_month
    elif callback_data == "month_last":
        return get_previous_month(current_year, current_month)
    elif callback_data == "month_previous":
        last_year, last_month = get_previous_month(current_year, current_month)
        return get_previous_month(last_year, last_month)
    else:
        return current_year, current_month
