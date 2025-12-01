import importlib
import os
import types

import pytest

from src import parsing


def reload_main_with_env(env: dict[str, str]) -> types.ModuleType:
    for key, value in env.items():
        os.environ[key] = value
    if "main" in list(globals()):
        import sys

        sys.modules.pop("main", None)
    import main  # type: ignore

    importlib.reload(main)
    return main


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.critical
@pytest.mark.fast
@pytest.mark.unit
def test_parse_expense_ok():
    assert parsing.parse_expense("Кофе 3.5") == ("Кофе", 3.5)
    assert parsing.parse_expense("Такси 250") == ("Такси", 250.0)
    assert parsing.parse_expense("Обед 12,40") == ("Обед", 12.40)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.critical
@pytest.mark.fast
@pytest.mark.unit
def test_parse_expense_invalid():
    from src.exceptions import ParsingError

    assert parsing.parse_expense("") is None
    try:
        parsing.parse_expense("просто текст")
        assert False, "Expected ParsingError"
    except ParsingError:
        pass
    try:
        parsing.parse_expense("нет суммы ")
        assert False, "Expected ParsingError"
    except ParsingError:
        pass
    assert parsing.parse_expense("  ") is None


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.unit
def test_allowlist_empty_all_allowed(monkeypatch):
    from src import auth

    monkeypatch.setenv("ALLOWED_USER_IDS", "")
    assert auth.is_user_allowed(123)


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.unit
def test_allowlist_specific_only_allowed(monkeypatch):
    from src import auth

    monkeypatch.setenv("ALLOWED_USER_IDS", "1, 2,3")
    assert auth.is_user_allowed(1)
    assert auth.is_user_allowed(2)
    assert auth.is_user_allowed(3)
    assert not auth.is_user_allowed(4)


@pytest.mark.fast
@pytest.mark.unit
def test_parse_multiple_expenses_semicolon():
    costs, failed = parsing.parse_multiple_expenses("Кофе 3.5; Такси 250")
    assert costs == [("Кофе", 3.5), ("Такси", 250.0)]
    assert failed == []

    costs, failed = parsing.parse_multiple_expenses("Обед 12,40; Ужин 15.5")
    assert costs == [("Обед", 12.40), ("Ужин", 15.5)]
    assert failed == []


@pytest.mark.fast
@pytest.mark.unit
def test_parse_multiple_expenses_newline():
    costs, failed = parsing.parse_multiple_expenses("Кофе 3.5\nТакси 250")
    assert costs == [("Кофе", 3.5), ("Такси", 250.0)]
    assert failed == []


@pytest.mark.fast
@pytest.mark.unit
def test_parse_multiple_expenses_single():
    costs, failed = parsing.parse_multiple_expenses("Кофе 3.5")
    assert costs == [("Кофе", 3.5)]
    assert failed == []


@pytest.mark.fast
@pytest.mark.unit
def test_parse_multiple_expenses_invalid():
    costs, failed = parsing.parse_multiple_expenses("")
    assert costs == []
    assert failed == []

    costs, failed = parsing.parse_multiple_expenses("просто текст")
    assert costs == []
    assert len(failed) == 1  # Ошибка парсинга

    costs, failed = parsing.parse_multiple_expenses("Кофе 3.5; invalid; Такси 250")
    assert costs == [("Кофе", 3.5), ("Такси", 250.0)]
    assert len(failed) == 1  # "invalid" не парсится
