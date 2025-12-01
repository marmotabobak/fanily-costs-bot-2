# ===== ПОЛЬЗОВАТЕЛЬСКИЕ СООБЩЕНИЯ =====

HELP_TEXT = (
    "Привет! Я бот для учёта расходов.\n\n"
    "Вводи траты в формате: <описание> <сумма>\n"
    "Можно ввести несколько расходов через ; или с новой строки:\n\n"
    "Примеры:\n"
    "- Кофе 3.5\n"
    "- Такси 250\n"
    "- Обед 12,40\n"
    "- Кофе 3.5; Такси 250; Обед 12,40\n"
    "- Кофе 3.5\n"
    "  Такси 250\n"
    "  Обед 12,40\n\n"
    "Используйте кнопки ниже для просмотра расходов:"
)

SUCCESS_SAVED_TEMPLATE = "✅ Расход сохранён: {description} — {amount_str}."
SUCCESS_MULTIPLE_SAVED_TEMPLATE = "✅ Сохранено {count} расходов:\n{details}"

ERROR_INVALID_FORMAT = "❌ Некорректный формат. Введите расход в формате: <описание> <сумма>."
ERROR_PROCESSING_TEMPLATE = "❌ Не удалось обработать сообщение: {err}."
ERROR_EMPTY_DESCRIPTION_OR_AMOUNT = "❌ Описание и сумма не могут быть пустыми."
ERROR_ACCESS_DENIED = "⛔ У вас нет доступа к этому боту."
ERROR_PARSING_TEMPLATE = "⚠️ Ошибки парсинга {count} записей:\n{details}"
ERROR_SAVING_TEMPLATE = "⚠️ Не удалось сохранить {count} записей:\n{details}"

# ===== СООБЩЕНИЯ ДЛЯ ПАРСИНГА =====

PARSING_ERROR_INVALID_FORMAT = "❌ Некорректный формат: ожидается 'описание сумма', получено: [{text}]"
PARSING_ERROR_INVALID_AMOUNT = "❌ Некорректный формат суммы: [{amount}]. Ошибка: [{error}]."

# ===== ЛОГИРОВАНИЕ =====

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"

# Логи инициализации
LOG_BOT_STARTING = "Starting bot by user_id=[{user_id}]..."
LOG_BOT_START_SUCCESS = "... /start successfully processed for user_id=[{user_id}]."
LOG_ACCESS_DENIED_START = "...Access denied for user_id=[{user_id}] on /start"
LOG_ACCESS_DENIED_MESSAGE = "Access denied for new message from user_id=[{user_id}]."

# Логи парсинга
LOG_SKIPPING_EMPTY_PART = "Skipping empty part: [{text}]."
LOG_SKIPPING_INVALID_PART = "Skipping invalid part: [{text}]."
LOG_PARSING_FAILED = "Parsing failed for the message: [{message}] from user_id=[{user_id}]"
LOG_SKIPPING_INVALID_PART_ERROR = "Skipping invalid part: [{part}]. Error: [{error}]."

# Логи базы данных
LOG_ADDING_EXPENSE = "Adding expense: [{description}] with amount=[{amount}] for user_id=[{user_id}]..."
LOG_EXPENSE_SAVED = "...expense [{description}] with amount=[{amount_str}] successfully saved for user_id=[{user_id}]."
LOG_FAILED_INSERT = "Failed to insert expense for user_id=[{user_id}]. Error: [{error}]."

# Логи конфигурации
LOG_ACCESS_RESTRICTED = "Access restricted to [{count}] user(s)."
LOG_ACCESS_OPEN = "Access open to all users (no ALLOWED_USER_IDS set)"
LOG_SKIPPING_USER_ID = "Skipping user id=[{user_id}] due to error: [{error}]."

# Логи окружения
LOG_ENV_TOKEN = "[ENV]: TELEGRAM_TOKEN=[{token}]"
LOG_ENV_LOG_LEVEL = "[ENV]: LOG_LEVEL=[{level}]"
LOG_ENV_USER_IDS = "[ENV]: ALLOWED_USER_IDS_RAW=[{user_ids}]"

# ===== БАЗА ДАННЫХ =====

DB_PATH_DEFAULT = "expenses.db"
DB_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    created_at TEXT NOT NULL,
    user_id INTEGER NOT NULL
);
"""
DB_INSERT_SQL = "INSERT INTO expenses(description, amount, created_at, user_id) VALUES (?, ?, ?, ?)"

# Логи базы данных
LOG_DB_INITIALIZING = "Initializing database at [{path}]..."
LOG_DB_INITIALIZED = "...Database initialized."
LOG_DB_EXECUTING_SQL = "Executing SQL: [{sql}] with params=[{params}]..."
LOG_DB_INSERTED = "...Inserted expense with id=[{expense_id}]"

# ===== РАЗДЕЛИТЕЛИ =====

COSTS_SEPARATORS = (";", "\n")

# ===== КНОПКИ И ИНТЕРФЕЙС =====

# Кнопки
BUTTON_VIEW_EXPENSES = "📊 Показать расходы"
BUTTON_THIS_MONTH = "📅 Этот месяц"
BUTTON_LAST_MONTH = "📅 Прошлый месяц"
BUTTON_PREVIOUS_MONTH = "📅 Предыдущий месяц"
BUTTON_BACK_TO_MENU = "🔙 Назад в меню"

# Сообщения для отображения расходов
EXPENSES_HEADER_TEMPLATE = "📊 Расходы за {month_name} {year}:\n\n"
EXPENSES_USER_HEADER_TEMPLATE = "👤 {user_name}:\n"
EXPENSES_ITEM_TEMPLATE = "  • {description} — {amount_str} ({date})\n"
EXPENSES_TOTAL_TEMPLATE = "\n💰 Итого: {total_amount_str}"
EXPENSES_EMPTY_TEMPLATE = "📭 Расходов за {month_name} {year} не найдено."

# Названия месяцев
MONTH_NAMES = [
    "январь",
    "февраль",
    "март",
    "апрель",
    "май",
    "июнь",
    "июль",
    "август",
    "сентябрь",
    "октябрь",
    "ноябрь",
    "декабрь",
]

# SQL запросы для получения расходов
DB_GET_EXPENSES_BY_MONTH_SQL = """
SELECT description, amount, created_at, user_id
FROM expenses
WHERE strftime('%Y-%m', created_at) = ?
ORDER BY created_at DESC
"""

DB_GET_EXPENSES_BY_USER_AND_MONTH_SQL = """
SELECT description, amount, created_at
FROM expenses
WHERE user_id = ? AND strftime('%Y-%m', created_at) = ?
ORDER BY created_at DESC
"""
