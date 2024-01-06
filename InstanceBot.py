from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from Config import TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.bot.api import TelegramAPIServer

storage = MemoryStorage()

bot = Bot(
  token=TOKEN,
  parse_mode='HTML',
  server=TelegramAPIServer(
      f"http://localhost:8081/bot{{token}}/{{method}}", # URL используется здесь как константа для упрощения понимания. Такое лучше хранить в .env-файле.
      f"http://localhost:8080/file/bot{{token}}/{{path}}"
    )
)
dp = Dispatcher(bot, storage=storage)
