import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher

from src.bot import setup_bot_and_dispatcher


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if token is None:
        logging.error("No token supplied, use BOT_TOKEN environment variable")
        return

    bot = Bot(token)
    dispatcher = Dispatcher()
    await setup_bot_and_dispatcher(bot, dispatcher)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
