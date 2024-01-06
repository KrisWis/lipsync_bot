from aiogram.utils import executor
from aiogram.types import BotCommand
""" Apscheluder используется для планирования различных задач с множеством различных функций и параметров планирования.
Триггер cron используется для периодического планирования задач, которые должны повторяться. 
Например, выполнение задачи в определенное время каждый день или выполнение задачи в определенные дни (например, с понедельника по пятницу). """
from apscheduler.triggers.cron import CronTrigger
from InstanceBot import bot, dp
from database.db import db
""" AsyncIOScheduler, который позволяет разработчикам легко планировать асинхронные функции и сопрограммы с помощью asyncio. 
Используя асинхронное выполнение, AsyncIOScheduler повышает общую производительность вашего приложения. 
Вместо ожидания завершения каждой задачи перед переходом к следующей, задачи могут выполняться одновременно, 
что приводит к более эффективному использованию ресурсов и более быстрому времени завершения. 
AsyncIOScheduler легко интегрируется с более широкой экосистемой asyncio, позволяя вам комбинировать его возможности с другими библиотеками и фреймворками async. """
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import handlers
import utils

async def on_startup(dp):
    # Инициализируем бд
    await db.create_pool()
    await db.create_tables()

    sch = AsyncIOScheduler(timezone='Europe/Moscow')

    # Добавляем в планировщик задание, чтобы он в каждые 0 часов по мск запускал функцию update_requests().
    sch.add_job(
        func=utils.scheduler.update_requests,
        trigger=CronTrigger(
            hour=0
        )
    )

    # print_jobs() распечатает отформатированный список заданий, их триггеры и время следующего выполнения.
    sch.print_jobs()

    # Запуск запланированных заданий
    sch.start()

    # Определяем команды и добавляем их в бота
    commands = [
        BotCommand(command='/start', description='Перезапустить бота'),
        BotCommand(command='/premium', description='Приобрести подписку'),
        BotCommand(command='/account', description='Информация о лимитах'),
        BotCommand(command='/create_video', description='Создание видео'),
        BotCommand(command='/help', description='Инструкция о том, как создать видео')
    ]

    await bot.set_my_commands(commands)

    handlers.hand_start.hand_add(dp)
    handlers.hand_buy.hand_add(dp)

    handlers.admin_mail.hand_add(dp)
    handlers.admin_start.hand_add(dp)

    print('Бот запущен')

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
