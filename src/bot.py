"""Bot initialization and main entry point."""

import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart

from . import auth, config, db, handlers

logger = logging.getLogger(__name__)


async def main() -> None:
    """Главная функция приложения. Инициализирует БД и запускает бота."""
    config.setup_logging()
    config.log_configuration()
    auth.log_access_control()

    db.init_db()

    bot = Bot(token=config.get_telegram_token(), parse_mode=None)
    dp = Dispatcher()

    dp.message.register(handlers.handle_start, CommandStart())
    dp.message.register(handlers.handle_text, F.text)

    # Обработчики для кнопок
    dp.callback_query.register(handlers.handle_view_expenses_callback, F.data == "view_expenses")
    dp.callback_query.register(handlers.handle_month_selection_callback, F.data.startswith("month_"))
    dp.callback_query.register(handlers.handle_back_to_menu_callback, F.data == "back_to_menu")

    await dp.start_polling(bot)
