"""Message handlers for the Family Costs Bot."""

import logging

from aiogram.types import CallbackQuery, Message

from . import auth, db, expense_display, keyboards, parsing, strings, utils

logger = logging.getLogger(__name__)


async def handle_start(message: Message) -> None:
    """Обработчик команды /start."""
    user_id = utils.get_user_id(message)
    logger.debug(strings.LOG_BOT_STARTING.format(user_id=user_id))

    if not auth.is_user_allowed(user_id):
        logger.warning(strings.LOG_ACCESS_DENIED_START.format(user_id=user_id))
        await utils.send_access_denied(message)
        return

    logger.info(strings.LOG_BOT_START_SUCCESS.format(user_id=user_id))
    keyboard = keyboards.get_main_keyboard()
    await message.answer(strings.HELP_TEXT, reply_markup=keyboard)


async def handle_text(message: Message) -> None:
    """Обработчик текстовых сообщений."""
    user_id = utils.get_user_id(message)
    logger.debug(f"Incoming message from user_id=[{user_id}]: [{message.text}].")

    if not auth.is_user_allowed(user_id):
        logger.warning(strings.LOG_ACCESS_DENIED_MESSAGE.format(user_id=user_id))
        await utils.send_access_denied(message)
        return

    costs, failed_costs = parsing.parse_multiple_expenses(message.text or "")

    if not costs and not failed_costs:
        logger.warning(strings.LOG_PARSING_FAILED.format(message=message.text, user_id=user_id))
        await message.answer(strings.ERROR_INVALID_FORMAT)
        return

    # Обрабатываем каждую запись и генерируем сообщения об успешных и неудачных записях в БД
    success_db_inserts_messages = []
    failed_db_inserts_insertions = []

    for description, amount in costs:
        try:
            logger.debug(strings.LOG_ADDING_EXPENSE.format(description=description, amount=amount, user_id=user_id))
            db.insert_expense(description=description, amount=amount, user_id=user_id)

            amount_str = f"{amount:.2f}".rstrip("0").rstrip(".")
            success_db_inserts_messages.append(
                strings.SUCCESS_SAVED_TEMPLATE.format(description=description, amount_str=amount_str)
            )

            logger.info(
                strings.LOG_EXPENSE_SAVED.format(description=description, amount_str=amount_str, user_id=user_id)
            )

        except Exception as err:
            logger.exception(strings.LOG_FAILED_INSERT.format(user_id=user_id, error=err))
            failed_db_inserts_insertions.append(strings.ERROR_PROCESSING_TEMPLATE.format(err=err))

    # Отправляем результат
    await utils.send_success_messages(message, success_db_inserts_messages)
    await utils.send_db_insert_error_messages(message, failed_db_inserts_insertions)
    await utils.send_parsing_errors(message, failed_costs)


async def handle_view_expenses_callback(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Показать расходы'."""
    user_id = callback.from_user.id
    logger.debug(f"View expenses callback from user_id=[{user_id}]")

    if not auth.is_user_allowed(user_id):
        logger.warning(strings.LOG_ACCESS_DENIED_MESSAGE.format(user_id=user_id))
        await callback.answer("⛔ У вас нет доступа к этому боту.")
        return

    keyboard = keyboards.get_month_selection_keyboard()
    await callback.message.edit_text("📊 Выберите месяц для просмотра расходов:", reply_markup=keyboard)
    await callback.answer()


async def handle_month_selection_callback(callback: CallbackQuery) -> None:
    """Обработчик выбора месяца."""
    user_id = callback.from_user.id
    logger.debug(f"Month selection callback from user_id=[{user_id}]: {callback.data}")

    if not auth.is_user_allowed(user_id):
        logger.warning(strings.LOG_ACCESS_DENIED_MESSAGE.format(user_id=user_id))
        await callback.answer("⛔ У вас нет доступа к этому боту.")
        return

    try:
        year, month = expense_display.get_month_from_callback(callback.data)
        expenses = db.get_expenses_by_month(year, month)

        formatted_expenses = expense_display.format_expenses_for_display(expenses, year, month)
        keyboard = keyboards.get_back_to_menu_keyboard()

        await callback.message.edit_text(formatted_expenses, reply_markup=keyboard)
        await callback.answer()

    except Exception as err:
        logger.exception(f"Error handling month selection: {err}")
        await callback.answer("❌ Ошибка при получении расходов.")
        await callback.message.edit_text(
            "❌ Произошла ошибка при получении расходов. Попробуйте позже.",
            reply_markup=keyboards.get_back_to_menu_keyboard(),
        )


async def handle_back_to_menu_callback(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Назад в меню'."""
    user_id = callback.from_user.id
    logger.debug(f"Back to menu callback from user_id=[{user_id}]")

    if not auth.is_user_allowed(user_id):
        logger.warning(strings.LOG_ACCESS_DENIED_MESSAGE.format(user_id=user_id))
        await callback.answer("⛔ У вас нет доступа к этому боту.")
        return

    keyboard = keyboards.get_main_keyboard()
    await callback.message.edit_text(strings.HELP_TEXT, reply_markup=keyboard)
    await callback.answer()
