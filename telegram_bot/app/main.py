import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.api_client import APIClient
from app.config import settings
from app.handlers import advice, start, match, events, common
from app.infrastructure.client import RabbitMQClient


from app import deps

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


async def on_startup(bot: Bot):
    deps.rabbitmq_client = RabbitMQClient(
        url=settings.RABBITMQ_URL,
        timeout=settings.RABBITMQ_TIMEOUT,
    )
    await deps.rabbitmq_client.start()
    logger.info("RabbitMQ client started")

    deps.api_client = APIClient(
        base_url=settings.API_URL,
        use_rabbitmq=True,
        rabbitmq_client=deps.rabbitmq_client,
    )
    await deps.api_client.start()
    logger.info("API client started")

    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="new_match", description="Создать новый матч"),
        BotCommand(command="current", description="Текущий матч"),
        BotCommand(command="complete", description="Завершить матч"),
        BotCommand(command="advice", description="Совет тренера"),
        BotCommand(command="cancel", description="Отменить операцию"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands set")


async def on_shutdown(bot: Bot):

    if deps.api_client:
        await deps.api_client.stop()
        logger.info("API client stopped")

    if deps.rabbitmq_client:
        await deps.rabbitmq_client.stop()
        logger.info("RabbitMQ client stopped")

    await bot.session.close()
    logger.info("Bot session closed")


async def main():
    setup_logging()

    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(start.router)
    dp.include_router(match.router)
    dp.include_router(events.router)
    dp.include_router(advice.router)
    dp.include_router(common.router)

    logger.info("Bot started")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
