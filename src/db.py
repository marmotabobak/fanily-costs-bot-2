import logging
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from . import strings

logger = logging.getLogger(__name__)


@dataclass
class Expense:
    """Модель данных расхода."""

    id: int
    description: str
    amount: float
    created_at: str
    user_id: int


def _get_connection(db_path: str) -> sqlite3.Connection:
    """Создаёт соединение с БД и возвращает его."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = strings.DB_PATH_DEFAULT) -> None:
    """Создаёт таблицу расходов, если она не существует."""
    logger.debug(strings.LOG_DB_INITIALIZING.format(path=db_path))
    conn = _get_connection(db_path)
    try:
        conn.execute(strings.DB_CREATE_TABLE_SQL)
        conn.commit()
        logger.info(strings.LOG_DB_INITIALIZED)
    finally:
        conn.close()


def insert_expense(
    description: str,
    amount: float,
    user_id: int,
    db_path: str = strings.DB_PATH_DEFAULT,
) -> int:
    """Вставляет расход в БД и возвращает его id."""
    if not description or not amount:
        raise ValueError(strings.ERROR_EMPTY_DESCRIPTION_OR_AMOUNT)

    conn = _get_connection(db_path)
    try:
        created_at = datetime.now(UTC).isoformat(timespec="seconds")
        sql_params = (description, float(amount), created_at, user_id)
        logger.debug(strings.LOG_DB_EXECUTING_SQL.format(sql=strings.DB_INSERT_SQL, params=sql_params))
        cur = conn.execute(strings.DB_INSERT_SQL, sql_params)
        conn.commit()
        new_id = int(cur.lastrowid)
        logger.info(strings.LOG_DB_INSERTED.format(expense_id=new_id))
        return new_id
    finally:
        conn.close()


def get_expenses_by_month(
    year: int,
    month: int,
    db_path: str = strings.DB_PATH_DEFAULT,
) -> list[Expense]:
    """Получает все расходы за указанный месяц."""
    conn = _get_connection(db_path)
    try:
        month_str = f"{year:04d}-{month:02d}"
        logger.debug(f"Getting expenses for month: {month_str}")

        cur = conn.execute(strings.DB_GET_EXPENSES_BY_MONTH_SQL, (month_str,))
        rows = cur.fetchall()

        expenses = []
        for row in rows:
            expense = Expense(
                id=0,  # Не используется в этом контексте
                description=row["description"],
                amount=row["amount"],
                created_at=row["created_at"],
                user_id=row["user_id"],
            )
            expenses.append(expense)

        logger.info(f"Found {len(expenses)} expenses for {month_str}")
        return expenses
    finally:
        conn.close()


def get_expenses_by_user_and_month(
    user_id: int,
    year: int,
    month: int,
    db_path: str = strings.DB_PATH_DEFAULT,
) -> list[Expense]:
    """Получает расходы конкретного пользователя за указанный месяц."""
    conn = _get_connection(db_path)
    try:
        month_str = f"{year:04d}-{month:02d}"
        logger.debug(f"Getting expenses for user {user_id} for month: {month_str}")

        cur = conn.execute(strings.DB_GET_EXPENSES_BY_USER_AND_MONTH_SQL, (user_id, month_str))
        rows = cur.fetchall()

        expenses = []
        for row in rows:
            expense = Expense(
                id=0,  # Не используется в этом контексте
                description=row["description"],
                amount=row["amount"],
                created_at=row["created_at"],
                user_id=user_id,
            )
            expenses.append(expense)

        logger.info(f"Found {len(expenses)} expenses for user {user_id} for {month_str}")
        return expenses
    finally:
        conn.close()
