import logging
from uuid import UUID

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app import deps
from app.keyboards.actions import get_advice_keyboard

logger = logging.getLogger(__name__)

router = Router(name="advice")


@router.message(Command("advice"))
async def cmd_advice(message: Message):
    chat_id = message.chat.id

    if not deps.api_client:
        await message.answer("Сервис временно недоступен")
        return

    try:
        matches = await deps.api_client.get_live_match_by_chat_id(chat_id)
        if not matches:
            await message.answer("Нет активного матча. Создайте новый: /new_match")
            return

        match = matches[0]
        match_id = UUID(match["id"])

        status_msg = await message.answer("Генерирую совет тренера...")

        advice = await deps.api_client.request_advice(match_id, chat_id)

        await status_msg.delete()

        text = (
            f"Совет тренера\n\n"
            f"{advice}\n\n"
            f"{match['team_a_name']} vs {match['team_b_name']}\n"
            f"Счет: {match['score_a']}:{match['score_b']} (сет {match['current_set']})"
        )

        await message.answer(
            text,
            reply_markup=get_advice_keyboard(),
        )
    except Exception as e:
        logger.error(f"Error in cmd_advice: {e}")
        await message.answer("Ошибка получения совета. Попробуйте позже.")


@router.callback_query(F.data == "advice")
async def callback_advice(callback: CallbackQuery):
    chat_id = callback.message.chat.id

    if not deps.api_client:
        await callback.message.edit_text("Сервис временно недоступен")
        await callback.answer()
        return

    try:
        matches = await deps.api_client.get_live_match_by_chat_id(chat_id)
        if not matches:
            await callback.message.edit_text("Нет активного матча.")
            await callback.answer()
            return

        match = matches[0]
        match_id = UUID(match["id"])

        await callback.message.edit_text("Генерирую совет тренера...")

        advice = await deps.api_client.request_advice(match_id, chat_id)

        text = (
            f"Совет тренера\n\n"
            f"{advice}\n\n"
            f"{match['team_a_name']} vs {match['team_b_name']}\n"
            f"Счет: {match['score_a']}:{match['score_b']} (сет {match['current_set']})"
        )

        await callback.message.edit_text(
            text,
            reply_markup=get_advice_keyboard(),
        )
    except Exception as e:
        logger.error(f"Error in callback_advice: {e}")
        await callback.message.edit_text("Ошибка получения совета")
    finally:
        await callback.answer()


@router.callback_query(F.data == "advice:refresh")
async def callback_advice_refresh(callback: CallbackQuery):
    await callback_advice(callback)
