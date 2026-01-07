import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers
from database.db import init_db



BOT_TOKEN = '8464029782:AAGKTBfSv4cEh_opANgHHMrR-EmVNKBQS44'

async def main():
    print("Bot ishga tushmoqda...")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    await init_db()
    register_user_handlers(dp, bot)
    register_admin_handlers(dp, bot)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        await bot.session.close()
        print("Bot ishini to'xtatmoqda...")

if __name__ == "__main__":
    asyncio.run(main())
