import logging
from uuid import UUID
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from app import deps
from app.api_client import ConflictError, NotFoundError
from app.keyboards.actions import (
    get_action_keyboard,
    get_event_confirmation_keyboard,
    get_player_keyboard,
    get_result_keyboard,
)


class RecordEventState(StatesGroup):
    selecting_action = State()
    selecting_result = State()
    selecting_player = State()
    confirming_event = State()


logger = logging.getLogger(__name__)

router = Router(name="event")


async def start_event_recording(
    message: Message | CallbackQuery,
    state: FSMContext,
    match_id: UUID,
):
    if not deps.api_client:
        logger.error("API client not available")
        return
    try:
        data_match = await deps.api_client.get_match(match_id=match_id)
        print(f"DEBUG: get_match response keys: {data_match.keys()}")
        print(f"DEBUG: Full response: {data_match}")
        composition_a = data_match["composition_a"]
        composition_b = data_match["composition_b"]
        await state.update_data(
            composition_a=composition_a,
            composition_b=composition_b,
            active_match_id=match_id,
        )
        await state.set_state(RecordEventState.selecting_action)
        if isinstance(message, CallbackQuery):
            target = message.message
            await message.answer()
        else:
            target = message
        await target.answer(
            text="Выберите действие:",
            reply_markup=get_action_keyboard(),
        )
    except NotFoundError:
        await target.answer("Матч не найден. Возможно, он завршен")
        await state.clear()
        return
    except Exception as e:
        await target.answer("Ошибка загрузки матча")
        return


@router.callback_query(RecordEventState.selecting_action, F.data.startswith("action:"))
async def process_action_selection(callback: CallbackQuery, state: FSMContext):
    action_type = callback.data.split(":")[1]
    await state.update_data(action_type=action_type)
    await state.set_state(RecordEventState.selecting_result)
    await callback.message.edit_text(
        text=f"Действие: {action_type}\n\nВыберите результат:",
        reply_markup=get_result_keyboard(action_type),
    )
    await callback.answer()


@router.callback_query(RecordEventState.selecting_result, F.data.startswith("result:"))
async def process_result_selection(callback: CallbackQuery, state: FSMContext):
    result = callback.data.split(":")[2]
    action_type = callback.data.split(":")[1]
    data = await state.get_data()
    if data["action_type"] != action_type:
        await state.clear()
        await callback.message.edit_text("Ошибка состояния. Начните заново: /new_match")
        await callback.answer()
        return
    await state.update_data(result=result)
    composition_a = data["composition_a"]
    composition_b = data["composition_b"]

    all_players = composition_a + composition_b
    await state.set_state(RecordEventState.selecting_player)
    await callback.message.edit_text(
        text=f"Действие:{action_type}\nРезультат:{result}\n\nВыберите игрока",
        reply_markup=get_player_keyboard(all_players),
    )
    await callback.answer()


@router.callback_query(RecordEventState.selecting_player, F.data.startswith("player:"))
async def process_player_selection(callback: CallbackQuery, state: FSMContext):
    player = callback.data.split(":")[1]
    player_number = int(player)
    data = await state.get_data()
    composition_a = data["composition_a"]
    team_id = 1 if player_number in composition_a else 2
    await state.update_data(player_number=player_number, team_id=team_id)
    report = (
        f"Действие: {data['action_type']}\n\n"
        f"Результат: {data['result']}\n\n"
        f"Игрок: №{player_number} (Команда {team_id})\n\n"
    )
    await state.set_state(RecordEventState.confirming_event)
    await callback.message.edit_text(
        text=report + "Подтвердить запись события?",
        reply_markup=get_event_confirmation_keyboard(),
    )
    await callback.answer()


@router.callback_query(
    RecordEventState.confirming_event, F.data.startswith("confirm_event:")
)
async def process_event_confirmation(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(":")[1]
    if action == "no":
        data = await state.get_data()
        active_match_id = data["active_match_id"]
        await callback.message.edit_text("Событие отменено")
        await callback.answer()
        await start_event_recording(callback, state, active_match_id)
        return

    if action == "yes":
        data = await state.get_data()
        active_match_id = data["active_match_id"]
        player_number = data["player_number"]
        team_id = data["team_id"]
        action_type = data["action_type"]
        result = data["result"]

        if not deps.api_client:
            await callback.message.edit_text("Сервис временно недоступен")
            await callback.answer()
            return

        try:
            response = await deps.api_client.record_event(
                active_match_id,
                player_number,
                team_id,
                action_type,
                result,
            )
            score_a = response["score_a"]
            score_b = response["score_b"]
            current_set = response["current_set"]

            await callback.message.edit_text(
                f"Событие записано!\nСчет: {score_a}:{score_b} (Сет {current_set})"
            )
            await callback.answer()

            if response.get("status") == "COMPLETED":
                await callback.message.answer(
                    f"Матч завершен!\nПобедитель: {response.get('winner')}"
                )
                await state.clear()
            else:
                await start_event_recording(callback, state, active_match_id)
        except NotFoundError:
            await callback.message.edit_text("Матч не найден")
            await callback.answer()
            await state.clear()

        except ConflictError:
            await callback.message.edit_text("Матч уже завершён")
            await callback.answer()
            await state.clear()

        except Exception as e:
            await callback.message.edit_text("Ошибка записи. Попробуйте ещё раз.")
            await callback.answer()
