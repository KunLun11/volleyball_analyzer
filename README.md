# 🏐 Volleyball Analytics Platform

A comprehensive volleyball analytics service with real-time data processing, AI-powered insights, and a Telegram bot interface.

## 📋 Overview

This project is a full-stack volleyball analytics platform consisting of:

- **Backend** — FastAPI service for data processing and API endpoints
- **Frontend** — Modern SvelteKit web interface
- **Telegram Bot** — Interactive bot for volleyball statistics and notifications
- **Data Pipeline** — Kafka-based streaming architecture with ClickHouse analytics
- **AI Integration** — LLM-powered insights (OpenAI/Ollama support)

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Telegram  │────▶│   Backend   │◀────│   Frontend  │
│     Bot     │     │   (FastAPI) │     │  (SvelteKit)│
└─────────────┘     └──────┬──────┘     └──────▲──────┘
                           │                   │
                    ┌──────▼──────┐     ┌──────┴──────┐
                    │    Kafka    │────▶│  ClickHouse │
                    │  (Streaming)│     │ (Analytics) │
                    └──────▲──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  PostgreSQL │
                    │   (Storage) │
                    └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) >= 20.10
- [Docker Compose](https://docs.docker.com/compose/install/) >= 2.0
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd volleyball-analyzer
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

**Required environment variables:**

```ini
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=volleyball

# ClickHouse
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_PORT=8123
CLICKHOUSE_DB=volleyball
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Backend
APP_HOST=0.0.0.0
APP_PORT=8000

# LLM Configuration (choose one)
# Option 1: OpenAI
LLM_TYPE=openai
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30
OPENAI_MAX_RETRIES=3
OPENAI_MAX_TOKENS=1024

# Option 2: Ollama (local)
LLM_TYPE=ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=60
OLLAMA_MAX_RETRIES=3

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-here
BOT_TO_BACKEND_QUEUE=bot_to_backend
BOT_RESPONSES_QUEUE=bot_responses
```

### 3. Start All Services

```bash
docker-compose up -d
```

Wait for services to be healthy (approximately 1-2 minutes):

```bash
docker-compose ps
```

### 4. Access the Services

| Service       | URL                          | Description              |
|---------------|------------------------------|--------------------------|
| **Frontend**  | http://localhost:8080        | Web application          |
| **Backend API** | http://localhost:8000      | REST API & WebSocket     |
| **RabbitMQ**  | http://localhost:15672       | Management UI (guest/guest) |
| **ClickHouse**| http://localhost:8123        | HTTP interface           |
| **Kafka**     | localhost:9092               | Broker endpoint          |

## 📦 Services Description

### Backend (`/backend`)
- **Framework:** FastAPI
- **Python:** 3.11+
- **Features:** REST API, WebSocket, Kafka consumer/producer, RabbitMQ integration

### Frontend (`/frontend`)
- **Framework:** SvelteKit + Svelte 5
- **Styling:** TailwindCSS 4
- **Language:** TypeScript

### Telegram Bot (`/telegram_bot`)
- **Framework:** aiogram 3.x
- **Features:** Interactive commands, real-time notifications

### Data Infrastructure
- **PostgreSQL** — Primary data storage
- **ClickHouse** — Analytics and aggregations
- **Kafka** — Event streaming
- **RabbitMQ** — Message queue for bot communication
- **Ollama** — Local LLM inference (optional)

## 🔧 Development

### Running Individual Services

**Backend (local development):**
```bash
cd backend
uv sync
source .venv/bin/activate
uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (local development):**
```bash
cd frontend
npm install
npm run dev
```

**Telegram Bot (local development):**
```bash
cd telegram_bot
uv sync
source .venv/bin/activate
uv run python -m app.main
```

### Running Infrastructure Only

```bash
docker-compose up -d postgres clickhouse kafka rabbitmq zookeeper ollama
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes all data)
docker-compose down -v
```

## 📁 Project Structure

```
volleyball-analyzer/
├── backend/           # FastAPI backend service
├── frontend/          # SvelteKit web application
├── telegram_bot/      # Telegram bot service
├── infrastructure/    # Docker configs, init scripts, nginx
│   ├── postgresql/
│   ├── clickhouse/
│   ├── kafka/
│   ├── rabbitmq/
│   └── nginx/
├── kafka-logs/        # Kafka data directory
├── docker-compose.yml
└── README.md
```

## 🛠️ Troubleshooting

### Services won't start
```bash
# Check logs for errors
docker-compose logs backend
docker-compose logs telegram_bot

# Restart specific service
docker-compose restart backend
```

### Database connection issues
```bash
# Verify PostgreSQL is healthy
docker-compose ps postgres

# Check database initialization
docker-compose logs postgres | grep "ready to accept connections"
```

### Kafka connection issues
```bash
# Verify Kafka is running
docker-compose ps kafka

# Check Kafka topics
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```

## 📝 License

This project is provided as-is for educational and analytical purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Made with ❤️ for volleyball analytics**
