#!/bin/bash

# Скрипт деплоя Family Costs Bot на удаленный хост
# Использование: ./deploy.sh [remote_host] [remote_user] [remote_path]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Параметры по умолчанию
REMOTE_HOST=${1:-"v128387.hosted-by-vdsina.com"}
REMOTE_USER=${2:-"root"}
REMOTE_PATH=${3:-"/opt/family-costs-bot"}
LOCAL_PROJECT_DIR=$(pwd)

echo -e "${BLUE}🚀 Начинаем деплой Family Costs Bot...${NC}"

# Проверяем наличие необходимых файлов
echo -e "${YELLOW}📋 Проверяем необходимые файлы...${NC}"
required_files=("Dockerfile" "docker-compose.yml" "requirements.txt" "main.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Файл $file не найден!${NC}"
        exit 1
    fi
done

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Файл .env не найден. Создайте его на основе .env.example${NC}"
    echo -e "${YELLOW}   cp .env.example .env${NC}"
    echo -e "${YELLOW}   Затем отредактируйте .env с вашими настройками${NC}"
    exit 1
fi

# Проверяем подключение к удаленному хосту
echo -e "${YELLOW}🔌 Проверяем подключение к $REMOTE_HOST...${NC}"
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$REMOTE_USER@$REMOTE_HOST" exit 2>/dev/null; then
    echo -e "${RED}❌ Не удается подключиться к $REMOTE_HOST${NC}"
    echo -e "${YELLOW}💡 Убедитесь, что:${NC}"
    echo -e "   - SSH ключи настроены"
    echo -e "   - Хост доступен"
    echo -e "   - Пользователь $REMOTE_USER существует"
    exit 1
fi

# Создаем директорию на удаленном хосте
echo -e "${YELLOW}📁 Создаем директорию на удаленном хосте...${NC}"
ssh "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_PATH"

# Копируем файлы проекта
echo -e "${YELLOW}📤 Копируем файлы проекта...${NC}"
rsync -avz --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='venv' \
    --exclude='.venv' \
    --exclude='expenses.db' \
    --exclude='data/' \
    --exclude='.idea' \
    --exclude='.vscode' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    --exclude='Thumbs.db' \
    --exclude='*.tmp' \
    --exclude='*.swp' \
    --exclude='*.swo' \
    --exclude='*~' \
    --exclude='.env.local' \
    --exclude='.env.development' \
    --exclude='.env.test' \
    --exclude='.env.production' \
    "$LOCAL_PROJECT_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"

# Копируем .env файл
echo -e "${YELLOW}🔐 Копируем файл конфигурации...${NC}"
scp .env "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"

# Создаем директорию для данных
echo -e "${YELLOW}📊 Создаем директорию для данных...${NC}"
ssh "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_PATH/data"

# Останавливаем старые контейнеры
echo -e "${YELLOW}🛑 Останавливаем старые контейнеры...${NC}"
ssh "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && docker-compose down || true"

# Собираем и запускаем новые контейнеры
echo -e "${YELLOW}🔨 Собираем и запускаем контейнеры...${NC}"
ssh "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && docker-compose up --build -d"

# Проверяем статус
echo -e "${YELLOW}🔍 Проверяем статус контейнеров...${NC}"
ssh "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && docker-compose ps"

# Показываем логи
echo -e "${YELLOW}📋 Показываем последние логи...${NC}"
ssh "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && docker-compose logs --tail=20"

echo -e "${GREEN}✅ Деплой завершен успешно!${NC}"
echo -e "${BLUE}📝 Для мониторинга используйте:${NC}"
echo -e "   ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && docker-compose logs -f'"
echo -e "${BLUE}📝 Для остановки:${NC}"
echo -e "   ssh $REMOTE_USER@$REMOTE_HOST 'cd $REMOTE_PATH && docker-compose down'"
