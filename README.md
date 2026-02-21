# Volleyball Analytics Platform

Full-stack volleyball analytics service with real-time data processing and Telegram bot interface.

## Quick Start

### Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0

### 1. Clone and Configure

```bash
git clone <repository-url>
cd volleyball-analyzer
cp .env.example .env
```

### 2. Configure environment variables

Edit `.env` file and set required values:

```ini
# Telegram Bot (required)
TELEGRAM_BOT_TOKEN=your-bot-token-here

# LLM Configuration (choose one)
LLM_TYPE=ollama
# or
LLM_TYPE=openai
OPENAI_API_KEY=your-api-key-here
```

### 3. Start all services

```bash
docker-compose up -d
```

Wait 1-2 minutes for services to initialize, then check status:

```bash
docker-compose ps
```

### 4. Access services

| Service       | URL                    |
|---------------|------------------------|
| Frontend      | http://localhost:8080  |
| Backend API   | http://localhost:8000  |
| RabbitMQ UI   | http://localhost:15672 |
| ClickHouse    | http://localhost:8123  |

## Project Structure

```
volleyball-analyzer/
├── backend/           # FastAPI backend
├── frontend/          # SvelteKit web app
├── telegram_bot/      # Telegram bot
├── infrastructure/    # Docker configs & init scripts
└── docker-compose.yml
```

## Development

### Run backend locally

```bash
cd backend
uv sync
source .venv/bin/activate
uv run python -m uvicorn app.main:app --reload
```

### Run frontend locally

```bash
cd frontend
npm install
npm run dev
```

### View logs

```bash
docker-compose logs -f backend
```

### Stop services

```bash
docker-compose down
```

## Troubleshooting

**Services won't start:**
```bash
docker-compose logs backend
docker-compose restart backend
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up -d
```
