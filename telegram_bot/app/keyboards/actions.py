from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def _get_builder(
    buttons: list[tuple[str, str]],
    row_width: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        builder.button(text=text, callback_data=callback_data)
    builder.adjust(row_width)
    return builder.as_markup()


def get_action_keyboard() -> InlineKeyboardMarkup:
    return _get_builder(
        [
            ("Подача", "action:serve"),
            ("Атака", "action:attack"),
            ("Блок", "action:block"),
        ],
        row_width=3,
    )


def get_result_keyboard(action_type: str) -> InlineKeyboardMarkup:
    return _get_builder(
        [
            ("Забито", f"result:{action_type}:scored"),
            ("Нейтрально", f"result:{action_type}:neutral"),
            ("Ошибка", f"result:{action_type}:error"),
        ],
        row_width=3,
    )


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    return _get_builder(
        [
            ("Да", "confirm_match:yes"),
            ("Нет", "confirm_match:no"),
        ],
        row_width=2,
    )


def get_event_confirmation_keyboard() -> InlineKeyboardMarkup:
    return _get_builder(
        [
            ("Да", "confirm_event:yes"),
            ("Нет", "confirm_event:no"),
        ],
        row_width=2,
    )


def get_complete_keyboard() -> InlineKeyboardMarkup:
    return _get_builder(
        [
            ("Завершить", "complete:yes"),
            ("Отмена", "complete:no"),
        ],
        row_width=2,
    )


def get_player_keyboard(players: list[int]) -> InlineKeyboardMarkup:
    buttons = [(str(num), f"player:{num}") for num in players]
    return _get_builder(buttons, row_width=3)


def get_match_keyboard() -> InlineKeyboardMarkup:
    return _get_builder(
        [
            ("Совет тренера", "advice"),
            ("Статистика", "stats"),
            ("Записать событие", "record_event"),
            ("Завершить матч", "complete_match"),
        ],
        row_width=2,
    )


def get_advice_keyboard() -> InlineKeyboardMarkup:
    return _get_builder(
        [
            ("Ещё совет", "advice:refresh"),
            ("Записать событие", "record_event"),
            ("Завершить матч", "complete_match"),
        ],
        row_width=2,
    )
