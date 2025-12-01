import sqlite3
from types import SimpleNamespace

import pytest

from src import handlers
from src.db import init_db
from src.strings import ERROR_ACCESS_DENIED, SUCCESS_SAVED_TEMPLATE


class DummyMessage:
    def __init__(self, user_id: int | None, text: str | None):
        self.from_user = SimpleNamespace(id=user_id) if user_id is not None else None
        self.text = text
        self._answers: list[str] = []

    async def answer(self, text: str):
        self._answers.append(text)

    @property
    def answers(self) -> list[str]:
        return self._answers


@pytest.mark.asyncio
@pytest.mark.parametrize("message_text", ("/start", "Кофе 10"))
async def test_access_denied(monkeypatch, message_text):
    from src import auth

    monkeypatch.setattr(auth, "is_user_allowed", lambda _uid: False)
    msg = DummyMessage(user_id=1, text=message_text)
    if message_text == "/start":
        await handlers.handle_start(msg)
    else:
        await handlers.handle_text(msg)
    assert msg.answers[-1] == ERROR_ACCESS_DENIED


@pytest.mark.asyncio
async def test_on_text_invalid_format(monkeypatch):
    from src import auth

    monkeypatch.setattr(auth, "is_user_allowed", lambda _uid: True)
    msg = DummyMessage(user_id=1, text="invalid message")
    await handlers.handle_text(msg)
    # Теперь ожидаем сообщение об ошибке парсинга
    assert any("Ошибки парсинга" in ans for ans in msg.answers)


@pytest.mark.asyncio
async def test_on_text_success(monkeypatch):
    from src import auth, db

    monkeypatch.setattr(auth, "is_user_allowed", lambda _uid: True)
    monkeypatch.setattr(db, "insert_expense", lambda **kwargs: 1)
    msg = DummyMessage(user_id=1, text="Кофе 12.5")
    await handlers.handle_text(msg)
    assert any(ans.startswith(SUCCESS_SAVED_TEMPLATE.split(": ")[0]) for ans in msg.answers)


@pytest.mark.asyncio
async def test_e2e_full_flow_with_real_db(tmp_path, monkeypatch):
    from src import auth

    monkeypatch.setattr(auth, "is_user_allowed", lambda _uid: True)
    monkeypatch.chdir(tmp_path)
    init_db()
    msg = DummyMessage(user_id=1, text="Кофе 10.5")
    await handlers.handle_text(msg)
    assert any(ans.startswith(SUCCESS_SAVED_TEMPLATE.split(": ")[0]) for ans in msg.answers)

    # Проверяем, что запись действительно попала в БД "expenses.db" в tmp_path
    db_file = tmp_path / "expenses.db"
    assert db_file.exists()
    conn = sqlite3.connect(db_file)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT description, amount FROM expenses ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        assert row is not None
        assert row["description"] == "Кофе"
        assert row["amount"] == 10.5
    finally:
        conn.close()


@pytest.mark.asyncio
async def test_e2e_multiple_expenses_success(monkeypatch):
    from src import auth, db

    monkeypatch.setattr(auth, "is_user_allowed", lambda _uid: True)
    monkeypatch.setattr(db, "insert_expense", lambda **kwargs: 1)
    msg = DummyMessage(user_id=1, text="Кофе 3.5; Такси 250")
    await handlers.handle_text(msg)

    # Проверяем, что есть сообщение о сохранении нескольких расходов
    assert any("Сохранено 2 расходов" in ans for ans in msg.answers)
    assert any("Кофе — 3.5" in ans for ans in msg.answers)
    assert any("Такси — 250" in ans for ans in msg.answers)


@pytest.mark.asyncio
async def test_e2e_multiple_expenses_with_errors(monkeypatch):
    from src import auth, db

    def mock_insert(description, amount, **kwargs):
        if description == "Ошибка":
            raise ValueError("Test error")
        return 1

    monkeypatch.setattr(auth, "is_user_allowed", lambda _uid: True)
    monkeypatch.setattr(db, "insert_expense", mock_insert)
    msg = DummyMessage(user_id=1, text="Кофе 3.5; Ошибка 100; Такси 250")
    await handlers.handle_text(msg)

    # Проверяем успешные записи
    assert any("Сохранено 2 расходов" in ans for ans in msg.answers)
    assert any("Кофе — 3.5" in ans for ans in msg.answers)
    assert any("Такси — 250" in ans for ans in msg.answers)

    # Проверяем сообщение об ошибке
    assert any("Не удалось сохранить 1 записей" in ans for ans in msg.answers)
    assert any("Test error" in ans for ans in msg.answers)
