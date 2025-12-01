PYTHON := python
PIP := pip

.PHONY: install run fmt lint pre-commit test

install:
	$(PIP) install -r requirements.txt
	$(PIP) install black isort flake8 pre-commit pytest

run:
	@if [ -f .env ]; then \
		set -a; \
		source .env; \
		set +a; \
	fi; \
	$(PYTHON) main.py

fmt:
	isort --skip ".venv" --skip "venv" .
	black --extend-exclude '/\\.venv/' --extend-exclude '/venv/' .

lint:
	flake8 --exclude .venv,venv --max-line-length 120 .

pre-commit:
	pre-commit install
	pre-commit run --all-files

# Оптимизированные настройки параллельности
UNIT_JOBS ?= 2  # Для unit тестов: 1-2 потока (быстрые, I/O bound)
ASYNC_JOBS ?= 4  # Для async тестов: 2-4 потока (медленные, CPU bound)
ALL_JOBS ?= 6  # Для всех тестов: 4-6 потоков (смешанные)

test:
	PYTHONPATH=. pytest -q -n $(ALL_JOBS)

# Быстрые тесты для коммитов (unit тесты, 2 потока)
test-fast:
	PYTHONPATH=. pytest -q -m "fast" -n $(UNIT_JOBS)

# Критически важные тесты (unit тесты, 2 потока)
test-critical:
	PYTHONPATH=. pytest -q -m "critical" -n $(UNIT_JOBS)

# Медленные тесты (async, integration, e2e, 4 потока)
test-slow:
	PYTHONPATH=. pytest -q -m "slow" -n $(ASYNC_JOBS)

# Все тесты кроме медленных (unit + некоторые integration, 4 потока)
test-quick:
	PYTHONPATH=. pytest -q -m "not slow" -n $(ASYNC_JOBS)

# Только unit тесты (2 потока)
test-unit:
	PYTHONPATH=. pytest -q -m "unit" -n $(UNIT_JOBS)

# Только integration тесты (4 потока)
test-integration:
	PYTHONPATH=. pytest -q -m "integration" -n $(ASYNC_JOBS)

# Только e2e тесты (4 потока)
test-e2e:
	PYTHONPATH=. pytest -q -m "e2e" -n $(ASYNC_JOBS)

# Только async тесты (4 потока)
test-async:
	PYTHONPATH=. pytest -q tests/test_async.py tests/test_e2e.py tests/test_integration.py -n $(ASYNC_JOBS)

# Последовательное выполнение (для отладки)
test-serial:
	PYTHONPATH=. pytest -q

# Быстрые тесты последовательно (для pre-commit)
test-fast-serial:
	PYTHONPATH=. pytest -q -m "fast"

# Тесты с кастомным количеством потоков
test-custom:
	@echo "Usage: make test-custom JOBS=N"
	@echo "Example: make test-custom JOBS=8"
	PYTHONPATH=. pytest -q -n $(JOBS)
