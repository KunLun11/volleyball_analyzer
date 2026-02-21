from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


router = Router(name="start")


def get_start_keyboard() -> ReplyKeyboardMarkup:

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/new_match")],
            [KeyboardButton(text="/current")],
            [KeyboardButton(text="/complete")],
        ],
        resize_keyboard=True,
        # one_time_keyboard=False,
    )


@router.message(Command("start"))
async def cmd_start(message: Message):
    username = message.from_user.username
    await message.answer(
        f"Привет, {username}\n\n"
        "Я помогаю вести статистику волейбольных матчей.\n\n"
        "Доступные команды:\n"
        "/new_match — создать новый матч\n"
        "/current — продолжить текущий матч\n"
        "/complete — завершить матч\n\n"
        "Начните с /new_match",
        reply_markup=get_start_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Справка по командам:\n\n"
        "/start — начало работы\n"
        "/new_match — создать матч (ввод названий команд и составов)\n"
        "/current — показать текущий счёт и продолжить ввод событий\n"
        "/complete — завершить матч досрочно\n"
        "/cancel — отменить текущую операцию\n\n"
        "При создании матча:\n"
        "1. Введите название команды А\n"
        "2. Введите название команды Б\n"
        "3. Введите 6 номеров игроков команды А (1-99)\n"
        "4. Введите 6 номеров игроков команды Б (1-99)\n"
        "5. Подтвердите создание\n\n"
        "При записи события:\n"
        "1. Выберите действие (подача/атака/блок)\n"
        "2. Выберите результат (забито/нейтрально/ошибка)\n"
        "3. Выберите игрока\n"
        "4. Подтвердите запись"
    )
