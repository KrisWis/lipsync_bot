from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.payment import tariffs
from database.db import db


def premium():
    kb = InlineKeyboardMarkup(row_width=2)

    kb.add(InlineKeyboardButton(text='🎞 1 запрос - 30$', callback_data='p|1|30r'))

    for a, _ in enumerate(range(len(tariffs))):
        a += 1
        kb.add(
            InlineKeyboardButton(
                text=f'{tariffs[a]["name"]} - {tariffs[a]["amount"]}$ / мес',
                callback_data=f'p|{a}|{tariffs[a]["amount"]}'
            )
        )
    kb.add(InlineKeyboardButton(text='🎞 Купить запросы', callback_data='p|buy_requests'))

    return kb


def choice_method(tariff: int, amount):
    kb = InlineKeyboardMarkup(row_width=1)

    data = f'{tariff}|{amount}'

    kb.add(InlineKeyboardButton(text='⛓ Криптовалюта', callback_data=f'm|{data}'))

    kb.add(InlineKeyboardButton(text='Вернуться назад', callback_data='m|back'))
    return kb


def choice_crypto(tariff: int, amount):
    kb = InlineKeyboardMarkup(row_width=3)

    data = f'{tariff}|{amount}'

    values = ['USDT', 'USDC', 'TRX', 'TON']

    for value in values:
        kb.insert(InlineKeyboardButton(text=f'{value}', callback_data=f'v|{value}|{data}'))

    kb.add(InlineKeyboardButton(text='Вернуться назад', callback_data=f'm|back'))
    return kb


def check_payment_crypto(pay_url, invoice_id, tariff, amount, requests=None):
    kb = InlineKeyboardMarkup(row_width=1)

    data = f'{tariff}|{amount}'
    if requests:
        data = f'{tariff}|{amount}|{requests}'

    kb.add(InlineKeyboardButton(text='Оплатить', url=pay_url))
    kb.add(InlineKeyboardButton(text='Проверить оплату', callback_data=f'c|{invoice_id}|{data}'))
    kb.add(InlineKeyboardButton(text='Отменить', callback_data=f'm|back'))

    return kb


def choice_count_requests():
    kb = InlineKeyboardMarkup(row_width=5)

    for a, _ in enumerate(range(10)):
        a += 1
        kb.insert(
            InlineKeyboardButton(
                text=str(a),
                callback_data=f'p|{a}|{a * 30}r'
            )
        )

    kb.add(InlineKeyboardButton(text='Вернуться назад', callback_data='p|back'))

    return kb


def admin():
    kb = InlineKeyboardMarkup(row_width=3)

    kb.add(InlineKeyboardButton(text='📩 Рассылка', callback_data='a|mail'))
    kb.add(InlineKeyboardButton(text='📊 Статистика', callback_data='a|stata'))
    return kb


async def mail_setting():
    kb = InlineKeyboardMarkup(row_width=2)

    mail = await db.get_info_mail()

    if not mail[2]:
        kb.add(InlineKeyboardButton(text='Добавить фото', callback_data='t|photo|add'))
    else:
        kb.add(InlineKeyboardButton(text='Удалить фото', callback_data='t|photo|del'),
               InlineKeyboardButton(text='Показать фото', callback_data='t|photo|info'))

    if not mail[3]:
        kb.add(InlineKeyboardButton(text='Добавить кнопки', callback_data='t|buttons|add'))
    else:
        kb.add(InlineKeyboardButton(text='Удалить кнопки', callback_data='t|buttons|del'),
               InlineKeyboardButton(text='Показать кнопки', callback_data='t|buttons|info'))

    kb.add(InlineKeyboardButton(text='👀 Показать рассылку', callback_data='t|show'))
    kb.add(InlineKeyboardButton(text='🚀 Запустить рассылку', callback_data='t|run'))
    kb.add(InlineKeyboardButton(text='Вернуться в меню', callback_data='t|back'))
    return kb


async def user_mail(button_list):
    kb = InlineKeyboardMarkup(row_width=int(button_list[0]))

    for a, _ in enumerate(range(1, len(button_list))):

        index = a + 1
        r = button_list[index].split('|')
        kb.insert(InlineKeyboardButton(text=r[0], url=r[1]))

    return kb


async def admin_stata():
    kb = InlineKeyboardMarkup(row_width=4)

    kb.add(InlineKeyboardButton(text='День', callback_data='x|day'),
           InlineKeyboardButton(text='Неделя', callback_data='x|week'),
           InlineKeyboardButton(text='Месяц', callback_data='x|month'),
           InlineKeyboardButton(text='Все время', callback_data='x|all'))
    kb.add(InlineKeyboardButton(text='Вернуться в меню', callback_data='x|back'))
    return kb


def user_channels():
    kb = InlineKeyboardMarkup(row_width=2)

    channels = db.get_channels()

    a = 1
    for i in channels:
        kb.add(InlineKeyboardButton(text=i[3], url=i[2]))
        a += 1

    kb.add(InlineKeyboardButton(text='✅ Проверить подписку', callback_data='bub'))

    return kb


def admin_channels():
    kb = InlineKeyboardMarkup(row_width=2)

    kb.add(InlineKeyboardButton(text='➕ Добавить канал', callback_data='o|add'),
           InlineKeyboardButton(text='➖ Удалить канал', callback_data='o|del'))

    kb.add(InlineKeyboardButton(text='⚙️ Список каналов', callback_data='o|show'))
    kb.add(InlineKeyboardButton(text='Вернуться в меню', callback_data='o|back'))

    return kb


def channel_list():
    kb = InlineKeyboardMarkup(row_width=2)

    channels = db.get_channels()

    for i in channels:
        kb.insert(InlineKeyboardButton(text=i[3], callback_data=f'h|{i[3]}'))

    kb.add(InlineKeyboardButton(text='Вернуться в меню', callback_data='h|back'))
    return kb


def start_message():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Узнать о тарифах 💶', callback_data='start_premium'))
    return kb


def success_payment_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Получить инструкцию и загрузить видео 📼', callback_data='success_payment'))
    return kb


def offer_new_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Заказать ещё 🔖', callback_data='success_payment'))
    return kb
