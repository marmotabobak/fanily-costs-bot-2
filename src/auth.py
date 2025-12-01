"""User authorization for the Family Costs Bot."""

import logging

from . import strings
from .config import get_allowed_user_ids

logger = logging.getLogger(__name__)


def is_user_allowed(user_id: int | None) -> bool:
    """Проверяет, имеет ли пользователь с указанным id доступ к боту."""
    allowed_user_ids = get_allowed_user_ids()

    if not allowed_user_ids:
        return True
    if user_id is None:
        return False

    return user_id in allowed_user_ids


def log_access_control() -> None:
    """Логирует настройки контроля доступа."""
    allowed_user_ids = get_allowed_user_ids()

    if allowed_user_ids:
        logger.debug(strings.LOG_ACCESS_RESTRICTED.format(count=len(allowed_user_ids)))
    else:
        logger.debug(strings.LOG_ACCESS_OPEN)
