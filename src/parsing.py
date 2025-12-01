"""Expense parsing logic for the Family Costs Bot."""

import logging

from . import strings
from .exceptions import ParsingError

logger = logging.getLogger(__name__)


def parse_expense(message_text: str) -> tuple[str, float] | None:
    """
    Парсит сообщение на расход в формате: <описание> <сумма>.
    Возвращает кортеж (описание, сумма) или None, если сообщение некорректно.
    """
    text = message_text.strip()
    if not text:
        logger.warning(strings.LOG_SKIPPING_EMPTY_PART.format(text=text))
        return None

    parts = text.rsplit(maxsplit=1)
    if len(parts) != 2:
        logger.warning(strings.LOG_SKIPPING_INVALID_PART.format(text=text))
        raise ParsingError(strings.PARSING_ERROR_INVALID_FORMAT.format(text=text))

    description_raw, amount_raw = parts[0].strip(), parts[1].strip()
    if not description_raw or not amount_raw:
        logger.warning(strings.LOG_SKIPPING_INVALID_PART.format(text=text))
        raise ParsingError(strings.PARSING_ERROR_INVALID_FORMAT.format(text=text))

    normalized = amount_raw.replace(",", ".")
    try:
        amount = float(normalized)
    except Exception as err:
        logger.error(strings.LOG_SKIPPING_INVALID_PART.format(text=text))
        err_msg = strings.PARSING_ERROR_INVALID_AMOUNT.format(amount=amount_raw, error=err)
        raise ParsingError(strings.ERROR_PROCESSING_TEMPLATE.format(err=err_msg))

    return description_raw, amount


def parse_multiple_expenses(message_text: str) -> tuple[list[tuple[str, float]], list[str]]:
    """
    Парсит сообщение с несколькими сообщениями, разделёнными ';' или новой строкой.
    Возвращает список кортежей (описание, сумма) или пустой список, если ничего не найдено.
    """
    costs = []  # Успешно распарсенные расходы
    failed_costs = []  # Неудачно распарсенные расходы

    # Если нет разделителей, парсим как один расход
    if not any(separator in message_text for separator in strings.COSTS_SEPARATORS):
        try:
            cost = parse_expense(message_text)
            return ([cost], []) if cost else ([], [])
        except ParsingError as err:
            return ([], [str(err)])

    # Разделяем по ; или \n
    parts = []
    for separator in strings.COSTS_SEPARATORS:
        if separator in message_text:
            parts = [part.strip() for part in message_text.split(separator)]
            continue

    # Парсим каждую часть
    for part in parts:
        if not part:
            logger.warning(strings.LOG_SKIPPING_EMPTY_PART.format(text=part))
            continue

        try:
            parsed = parse_expense(part)
            if parsed:
                costs.append(parsed)
            else:
                failed_costs.append(part)
        except ParsingError as err:
            logger.error(strings.LOG_SKIPPING_INVALID_PART_ERROR.format(part=part, error=err))
            failed_costs.append(str(err))

    return costs, failed_costs
