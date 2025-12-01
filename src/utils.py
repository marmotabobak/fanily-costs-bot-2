"""Utility functions for the Family Costs Bot."""

from aiogram.types import Message

from . import strings


def get_user_id(message: Message) -> int | None:
    """Извлекает ID пользователя из сообщения."""
    return message.from_user.id if message.from_user else None


async def send_access_denied(message: Message) -> None:
    """Отправляет сообщение об отказе в доступе."""
    await message.answer(strings.ERROR_ACCESS_DENIED)


async def send_success_messages(message: Message, success_messages: list[str]) -> None:
    """Отправляет сообщения об успешном сохранении расходов."""
    if not success_messages:
        return

    if len(success_messages) == 1:
        await message.answer(success_messages[0])
    else:
        await message.answer(
            strings.SUCCESS_MULTIPLE_SAVED_TEMPLATE.format(
                count=len(success_messages), details="\n".join(success_messages)
            )
        )


async def send_db_insert_error_messages(message: Message, failed_messages: list[str]) -> None:
    """Отправляет сообщения об ошибках сохранения."""
    if failed_messages:
        await message.answer(
            strings.ERROR_SAVING_TEMPLATE.format(count=len(failed_messages), details="\n".join(failed_messages))
        )


async def send_parsing_errors(message: Message, failed_costs: list[str]) -> None:
    """Отправляет сообщения об ошибках парсинга."""
    if failed_costs:
        await message.answer(
            strings.ERROR_PARSING_TEMPLATE.format(count=len(failed_costs), details="\n".join(failed_costs))
        )
