# main.py
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import get_settings
from db import init_db
from handlers.start import router as start_router
from handlers.booking import router as booking_router
from handlers.reviews import router as reviews_router
from handlers.admin import router as admin_router
from handlers.info import router as info_router 

async def main():
    settings = get_settings()

    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN не задан в .env")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # добавили хранилище для FSM
    dp = Dispatcher(storage=MemoryStorage())

    # роутеры
    dp.include_router(start_router)
    dp.include_router(booking_router)
    dp.include_router(reviews_router)
    dp.include_router(admin_router)
    dp.include_router(info_router)

    # инициализируем базу
    await init_db()

    print("🤖 Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
