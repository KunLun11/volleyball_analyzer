from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_URL: str

    KAFKA_URL: str

    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int
    CLICKHOUSE_DB: str
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str

    APP_HOST: str
    APP_PORT: int

    LLM_TYPE: str = "openai"
    OPENAI_BASE_URL: str = (
        "https://agent.timeweb.cloud/api/v1/cloud-ai/agents/ae6c4372-4f7d-4e6a-9433-ffb568aa6685/v1"
    )
    OPENAI_API_KEY: str
    OPENAI_MODEL: str 
    OPENAI_TIMEOUT: float = 30.0
    OPENAI_MAX_RETRIES: int = 2
    OPENAI_MAX_TOKENS: int = 200

    OLLAMA_URL: str
    OLLAMA_MODEL: str
    OLLAMA_TIMEOUT: float
    OLLAMA_MAX_RETRIES: int

    ADVICE_MAX_LENGTH: int = 200

    RABBITMQ_URL: str
    BOT_TO_BACKEND_QUEUE: str
    BOT_RESPONSES_QUEUE: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
