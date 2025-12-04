# handlers/start.py
from aiogram import Router, types
from aiogram.filters import CommandStart, Command

from keyboards import main_menu_kb
from db import upsert_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user = message.from_user

    await upsert_user(
        tg_id=user.id,
        username=user.username,
        first_name=user.first_name,
        phone=None,
    )

    text = (
        f"Привет, {user.first_name or 'гость'}! 👋\n\n"
        "Я — RezMe, твой персональный гид по бронированию заведений в один клик! 🤖\n"
        "Здесь собраны лучшие заведения твоего города, бронируй без лишних звонков и сообщений ! 🤍\n"
        "💡 Просто выбери категорию — где хочешь провести сегодня вечер ?"
    )

    await message.answer(text, reply_markup=main_menu_kb)


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "ℹ️ Я помогу забронировать заведение:\n"
        "• Кафе/рестораны\n"
        "• Караоке\n"
        "• Боулинг\n\n"
        "Используй кнопки внизу экрана, чтобы начать 👇"
    )
    await message.answer(text, reply_markup=main_menu_kb)

@router.message(Command("myid"))
async def myid(message: types.Message):
    await message.answer(f"Ваш Telegram ID: <code>{message.from_user.id}</code>")