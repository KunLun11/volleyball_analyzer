# Volleyball Analytics Platform

Платформа для анализа волейбольных матчей с использованием искусственного интеллекта. Система обрабатывает статистику игр в реальном времени, предоставляет аналитику через веб-интерфейс и Telegram-бота.

## Описание проекта

**Volleyball Analytics Platform** — это полнофункциональная аналитическая система для волейбольных команд, тренеров и аналитиков. Платформа решает следующие задачи:

- **Сбор и обработка статистики** — автоматический сбор данных о матчах через Kafka и ClickHouse
- **AI-аналитика** — использование LLM (Ollama/OpenAI) для генерации инсайтов и рекомендаций
- **Telegram-бот** — удобный интерфейс для получения аналитики и уведомлений
- **Веб-дашборд** — визуализация статистики и метрик в реальном времени
- **Хранение данных** — надёжное хранение в PostgreSQL и ClickHouse

### Проблема, которую решает проект

Тренерам и аналитикам сложно оперативно получать и обрабатывать статистику матчей. Платформа автоматизирует этот процесс, предоставляя готовые инсайты и рекомендации через удобные интерфейсы.

## Архитектура проекта

```
┌─────────────────┐     ┌─────────────────────────────────────────────────────────────┐
│  Telegram Bot   │────▶│                     Backend (FastAPI)                       │
│  (Python)       │◀──▶│                                                             │
└─────────────────┘     │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
                        │  │  PostgreSQL │  │  ClickHouse │  │  LLM (Ollama/       │  │
                        │  │  (данные)   │  │  (аналитика)│  │   OpenAI)           │  │
                        │  └─────────────┘  └─────────────┘  └─────────────────────┘  │
                        └─────────────────────────────────────────────────────────────┘
                                                │           │
                                                ▼           ▼
┌─────────────────┐     ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Frontend      │◀──▶│     Nginx       │  │  RabbitMQ       │  │  Kafka          │
│   (SvelteKit)   │     │  (reverse proxy)│  │  (очереди)      │  │  (события)      │
└─────────────────┘     └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Поток данных

1. **Telegram-бот** принимает команды от пользователей и отправляет запросы в **Backend**
2. **Backend** обрабатывает запросы, используя:
   - **PostgreSQL** — для хранения основных данных
   - **ClickHouse** — для аналитических запросов
   - **LLM** — для генерации аналитических выводов
3. **Kafka** обрабатывает потоковые данные о матчах
4. **Kafka Consumer** записывает данные из Kafka в ClickHouse
5. **Frontend** отображает аналитику через **Nginx**

## Быстрый старт

### Требования

- Docker >= 20.10
- Docker Compose >= 2.0

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd volleyball-analyzer
cp .env.example .env
```

### 2. Настройка переменных окружения

Отредактируйте файл `.env` и установите необходимые значения:

```ini
# Telegram Bot (обязательно)
TELEGRAM_BOT_TOKEN=your-bot-token-here

# LLM Configuration (выберите один)
LLM_TYPE=ollama
# или
LLM_TYPE=openai
OPENAI_API_KEY=your-api-key-here
```

### 3. Запуск всех сервисов

```bash
docker compose up -d
```

Подождите 1-2 минуты для инициализации сервисов, затем проверьте статус:

```bash
docker compose ps
```

### 4. Доступ к сервисам

| Сервис        | URL                    |
|---------------|------------------------|
| Frontend      | http://localhost:8080  |
| Backend API   | http://localhost:8000  |
| RabbitMQ UI   | http://localhost:15672 |
| ClickHouse    | http://localhost:8123  |

## Структура проекта

```
volleyball-analyzer/
├── backend/           # FastAPI backend
├── frontend/          # SvelteKit web app
├── telegram_bot/      # Telegram bot
├── infrastructure/    # Docker configs & init scripts
└── docker-compose.yml
```

## Разработка

### Запуск backend локально

```bash
cd backend
uv sync
source .venv/bin/activate
uv run python -m uvicorn app.main:app --reload
```

### Запуск frontend локально

```bash
cd frontend
npm install
npm run dev
```

### Просмотр логов

```bash
docker compose logs -f backend
```

### Остановка сервисов

```bash
docker compose down
```

## Устранение проблем

**Сервисы не запускаются:**
```bash
docker compose logs backend
docker compose restart backend
```

**Полный сброс:**
```bash
docker compose down -v
docker compose up -d
```
