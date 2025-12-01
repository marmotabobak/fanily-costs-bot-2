"""Configuration management for the Family Costs Bot."""

import logging
import os

from . import strings

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Настраивает логирование на основе переменных окружения."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper().strip()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=strings.LOG_FORMAT,
    )


def get_telegram_token() -> str:
    """Возвращает токен Telegram бота из переменных окружения."""
    return os.getenv("BOT_TOKEN", "").strip()


def get_allowed_user_ids_raw() -> str:
    """Возвращает строку с разрешенными ID пользователей из переменных окружения."""
    return os.getenv("ALLOWED_USER_IDS", "").strip()


def parse_allowed_user_ids(raw: str) -> set[int]:
    """Конвертирует строку с id пользователей в множество id пользователей."""
    if not raw:
        return set()

    result: set[int] = set()

    for part in raw.split(","):
        if item := part.strip():
            try:
                result.add(int(item))
            except ValueError as err:
                logger.error(strings.LOG_SKIPPING_USER_ID.format(user_id=item, error=err))

    return result


def get_allowed_user_ids() -> set[int]:
    """Возвращает множество разрешенных ID пользователей."""
    return parse_allowed_user_ids(get_allowed_user_ids_raw())


def log_configuration() -> None:
    """Логирует конфигурацию приложения."""
    token = get_telegram_token()
    masked_token = token[:2] + "..." + token[-2:] if len(token) > 4 else "***"
    log_level = os.getenv("LOG_LEVEL", "INFO").upper().strip()
    user_ids_raw = get_allowed_user_ids_raw()

    logger.debug(strings.LOG_ENV_TOKEN.format(token=masked_token))
    logger.debug(strings.LOG_ENV_LOG_LEVEL.format(level=log_level))
    logger.debug(strings.LOG_ENV_USER_IDS.format(user_ids=user_ids_raw))
