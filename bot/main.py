import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
django.setup()

import asyncio
import signal


from aiogram import Bot, Dispatcher, BaseMiddleware
from bot.handlers import router
from bot.configuration import BOT_TOKEN, USER_IDS


class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data: dict):
        user = data.get("event_from_user")
        if user is None or user.id not in USER_IDS:
            return
        return await handler(event, data)
    
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.update.middleware(AccessMiddleware())
dp.include_router(router)




async def shutdown():
    await bot.session.close()


async def main():
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    for user_id in USER_IDS:
        try:
            await bot.send_message(user_id, "Bot started")
        except Exception as e:
            print(f"Failed to send message to user {user_id}: {e}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        raise