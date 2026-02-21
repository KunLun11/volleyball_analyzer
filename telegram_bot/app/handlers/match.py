from uuid import UUID
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app import deps
from app.api_client import APIClient, ConflictError, ValidationError
from app.keyboards.actions import get_complete_keyboard, get_confirmation_keyboard


router = Router(name="match")


class CreateMatchState(StatesGroup):
    waiting_team_a_name = State()
    waiting_team_b_name = State()
    waiting_composition_a = State()
    waiting_composition_b = State()
    confirming = State()


@router.message(Command("new_match"))
async def cmd_new_match(message: Message, state: FSMContext):
    await state.set_state(CreateMatchState.waiting_team_a_name)
    await message.answer(
        "Создание волейбольного матча \n\nВведите название первой команды (Команда А):"
    )


@router.message(CreateMatchState.waiting_team_a_name)
async def process_team_a_name(message: Message, state: FSMContext):
    text = message.text
    if len(text) < 1:
        await message.answer("Название не может быть пустым. Попробуйте ещё раз:")
        return
    await state.update_data(team_a_name=text)
    await state.set_state(CreateMatchState.waiting_team_b_name)
    await message.answer("Введите название второй команды (Команда Б):")


@router.message(CreateMatchState.waiting_team_b_name)
async def process_team_b_name(message: Message, state: FSMContext):
    text = message.text
    if len(text) < 1:
        await message.answer("Название не может быть пустым. Попробуйте ещё раз:")
        return
    await state.update_data(team_b_name=text)
    await state.set_state(CreateMatchState.waiting_composition_a)
    await message.answer("Введите 6 номеров команды А через пробел (1-99): 1 2 3 4 5 6")


@router.message(CreateMatchState.waiting_composition_a)
async def process_composition_a(message: Message, state: FSMContext):
    try:
        numbers = [int(t) for t in message.text.split()]
    except ValueError:
        await message.answer("Введите только числа через пробел. Попробуйте ещё раз:")
        return

    if len(numbers) != 6:
        await message.answer("Нужно ровно 6 номеров. Попробуйте ещё раз:")
        return

    if len(set(numbers)) != 6:
        await message.answer("Номера должны быть уникальными. Попробуйте ещё раз:")
        return
    for num in numbers:
        if not 1 <= num <= 99:
            await message.answer("Номера должны быть от 1 до 99. Попробуйте ещё раз:")
            return
    await state.update_data(composition_a=numbers)
    await state.set_state(CreateMatchState.waiting_composition_b)
    await message.answer("Введите 6 номеров команды Б через пробел (1-99): 1 2 3 4 5 6")


@router.message(CreateMatchState.waiting_composition_b)
async def process_composition_b(message: Message, state: FSMContext):
    try:
        numbers = [int(t) for t in message.text.split()]
    except ValueError:
        await message.answer("Введите только числа через пробел. Попробуйте ещё раз:")
        return
    if len(numbers) != 6:
        await message.answer("Нужно ровно 6 номеров. Попробуйте ещё раз:")
        return
    if len(set(numbers)) != 6:
        await message.answer("Номера должны быть уникальными. Попробуйте ещё раз:")
        return
    for num in numbers:
        if not 1 <= num <= 99:
            await message.answer("Номера должны быть от 1 до 99. Попробуйте ещё раз:")
            return
    await state.update_data(composition_b=numbers)

    data = await state.get_data()
    team_a_name = data.get("team_a_name")
    team_b_name = data.get("team_b_name")
    composition_a = data.get("composition_a")
    composition_b = data.get("composition_b")
    report = (
        "Проверьте данные матча:\n\n"
        f"Команда А: {team_a_name} \n"
        f"Состав: {composition_a[0]}, {composition_a[1]}, {composition_a[2]}, {composition_a[3]}, {composition_a[4]}, {composition_a[5]} \n"
        f"Команда Б: {team_b_name} \n"
        f"Состав: {composition_b[0]}, {composition_b[1]}, {composition_b[2]}, {composition_b[3]}, {composition_b[4]}, {composition_b[5]} \n\n"
        "Хотите подтвердить?"
    )
    await state.set_state(CreateMatchState.confirming)
    await message.answer(
        text=report,
        reply_markup=get_confirmation_keyboard(),
    )


@router.callback_query(CreateMatchState.confirming, F.data.startswith("confirm_match:"))
async def process_match_confirmation(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(":")[1]
    if action == "no":
        await callback.message.edit_text("Создание матча отменено.")
        await state.clear()
        await callback.answer()
        return

    if not deps.api_client:
        await callback.message.edit_text("Сервис временно недоступен")
        await callback.answer()
        await state.clear()
        return

    data = await state.get_data()

    try:
        result = await deps.api_client.create_match(
            team_a_name=data["team_a_name"],
            team_b_name=data["team_b_name"],
            composition_a=data["composition_a"],
            composition_b=data["composition_b"],
            chat_id=callback.message.chat.id,
        )
        match_id = result["id"]
        await callback.message.edit_text(
            f"Матч создан! \n"
            f"{data['team_a_name']} vs {data['team_b_name']} \n"
            "Сет 1, счет 0:0"
        )
        await callback.answer()
        from app.handlers.events import start_event_recording

        await start_event_recording(callback, state, UUID(match_id))
    except ValidationError as e:
        await callback.message.edit_text(f"Ошибка валидации: {e}")
        await callback.answer()
        await state.clear()

    except ConflictError as e:
        await callback.message.edit_text(f"{e}")
        await callback.answer()
        await state.clear()

    except Exception as e:
        await callback.message.edit_text(
            f"Ошибка при создании матча: {type(e).__name__}: {str(e)[:100]}"
        )
        await callback.answer()
        await state.clear()


@router.message(Command("current"))
async def cmd_current(message: Message, state: FSMContext):
    chat_id = message.chat.id

    if not deps.api_client:
        await message.answer("сервис временно недоступен")
        return

    try:
        matches = await deps.api_client.get_live_match_by_chat_id(chat_id)
        if not matches:
            await message.answer("Нет активного матча. \nСоздайте новый: /new_match")
            return
        match = matches[0]
        report = (
            f"Текущий матч\n\n"
            f"{match['team_a_name']} vs {match['team_b_name']}\n\n"
            f"Сет {match['current_set']}: {match['score_a']}:{match['score_b']}\n\n"
            f"Статус:{match['status']}"
        )
        await message.answer(report)
        from app.handlers.events import start_event_recording

        await start_event_recording(message, state, UUID(match["id"]))
    except Exception as e:
        await message.answer(f"Ошибка при получении данных{str(e)}")


@router.message(Command("complete"))
async def cmd_complete(message: Message, state: FSMContext):
    chat_id = message.chat.id

    if not deps.api_client:
        await message.answer("Сервис временно недоступен")
        return

    try:
        matches = await deps.api_client.get_live_match_by_chat_id(chat_id)
        if not matches:
            await message.answer("Нет активного матча.")
            return
        match = matches[0]
        match_id = match["id"]
        await message.answer(
            f"Завершить матч?\n\n"
            f"{match['team_a_name']} vs {match['team_b_name']}\n"
            f"Текущий счёт: {match['score_a']}:{match['score_b']}",
            reply_markup=get_complete_keyboard(),
        )
        await state.update_data(complete_match_id=match_id)
    except Exception as e:
        await message.answer("Ошибка при получении данных")


@router.callback_query(F.data.startswith("complete:"))
async def process_complete_confirmation(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(":")[1]
    if action == "no":
        await callback.message.edit_text("Отменено")
        await callback.answer()
        return
    data = await state.get_data()
    match_id = data.get("complete_match_id")
    if not match_id:
        await callback.message.edit_text("Ошибка: матч не найден")
        await callback.answer()
        return

    if not deps.api_client:
        await callback.message.edit_text("Сервис временно недоступен")
        await callback.answer()
        return

    try:
        result = await deps.api_client.complete_match(match_id=match_id)
        await callback.message.edit_text(
            f"Матч завершен!\n\nПобедитель: {result.get('winner')}"
        )
        await state.clear()
    except Exception as e:
        await callback.message.edit_text("Ошибка завершения матча")
    finally:
        await callback.answer()
