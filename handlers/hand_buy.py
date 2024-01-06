import datetime
from aiocryptopay import AioCryptoPay
import Config
from InstanceBot import bot
from aiogram import types, Dispatcher
from database.db import db
from keyboards import Keyboards
from utils import text, payment


async def choice_tariff(call: types.CallbackQuery):
    user_id = call.from_user.id
    temp = call.data.split('|')

    if temp[1] == 'buy_requests':
        await bot.edit_message_text(
            chat_id=user_id,
            text=text.payment_text,
            message_id=call.message.message_id,
            reply_markup=Keyboards.choice_count_requests()
        )

    else:
        await bot.edit_message_text(
            chat_id=user_id,
            text=text.payment_text,
            message_id=call.message.message_id,
            reply_markup=Keyboards.choice_method(int(temp[1]), temp[2])
        )


async def choice_method(call: types.CallbackQuery):
    user_id = call.from_user.id
    temp = call.data.split('|')

    if temp[1] != 'back':
        await bot.edit_message_text(
            chat_id=user_id,
            text=text.payment_text,
            message_id=call.message.message_id,
            reply_markup=Keyboards.choice_crypto(int(temp[1]), temp[2])
        )

    else:
        await bot.edit_message_text(
            chat_id=user_id,
            text=text.premium_text,
            message_id=call.message.message_id,
            reply_markup=Keyboards.premium()
        )


async def choice_crypto(call: types.CallbackQuery):
    user_id = call.from_user.id
    temp = call.data.split('|')

    crypto_bot = AioCryptoPay(token=Config.CRYPTO_BOT_TOKEN)

    amount = await payment.get_crypto_bot_sum(float(temp[3][:-1]), temp[1])
    invoice = await crypto_bot.create_invoice(
        asset=temp[1],
        amount=amount
    )
    await crypto_bot.close()

    try:
        var = int(temp[3])
        tariff = payment.tariffs[int(temp[2])]['name']

    except:
        tariff = f'🎞 Запросы ({temp[2]})'

    await bot.edit_message_text(
        chat_id=user_id,
        text=text.check_payment.format(
            tariff,
            f'{amount} <b>{temp[1]}</b>'
        ),
        message_id=call.message.message_id,
        reply_markup=Keyboards.check_payment_crypto(
            invoice.bot_invoice_url,
            invoice.invoice_id,
            tariff if 'Запросы' in tariff else int(temp[2]),
            amount,
            requests=temp[2] if 'Запросы' in tariff else None
        )
    )


async def check_payment(call: types.CallbackQuery):
    user_id = call.from_user.id
    temp = call.data.split('|')

    if await payment.check_crypto_bot_invoice(int(temp[1])):
        await call.answer(
            text=text.error_payment,
            show_alert=True
        )
        return

    if temp[2].isdigit():
        now = datetime.datetime.now()
        paid_date = now + datetime.timedelta(days=30)

        await db.update_paid_status(
            user_id=user_id,
            paid_type=temp[2],
            paid_date=paid_date,
            requests=payment.tariffs[int(temp[2])]['count']
        )

    else:
        await db.update_paid_status(
            user_id=user_id,
            requests=int(temp[4])
        )

    await bot.delete_message(user_id, call.message.message_id)

    await bot.send_message(
        chat_id=user_id,
        text=text.success_payment,
        reply_markup=Keyboards.success_payment_kb()
    )


def hand_add(dp: Dispatcher):
    dp.register_callback_query_handler(choice_tariff, lambda c: c.data and c.data.startswith('p'), state='*')
    dp.register_callback_query_handler(choice_method, lambda c: c.data and c.data.startswith('m'), state='*')
    dp.register_callback_query_handler(choice_crypto, lambda c: c.data and c.data.startswith('v'), state='*')
    dp.register_callback_query_handler(check_payment, lambda c: c.data and c.data.startswith('c'), state='*')
