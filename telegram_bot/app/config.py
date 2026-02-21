from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    API_URL: str = "http://localhost:8000"

    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    BOT_TO_BACKEND_QUEUE: str
    BOT_RESPONSES_QUEUE: str
    RABBITMQ_TIMEOUT: int

    class Config:
        env_file = ".env"


settings = Settings()
