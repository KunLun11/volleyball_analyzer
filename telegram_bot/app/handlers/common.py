from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


router = Router(name="common")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Нет активной операции для отмены.")
        return

    await state.clear()
    await message.answer("Операция отменена.\nНачните сначала: /new_match")


@router.message()
async def unknown_message(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state:
        await message.answer(
            "Вы находитесь в процессе создания матча или записи события.\n"
            "Завершите текущую операцию или отмените её: /cancel"
        )
    else:
        await message.answer("Не понимаю команду. Используйте /help для справки.")
