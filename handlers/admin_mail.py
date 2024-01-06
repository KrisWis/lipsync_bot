import asyncio
import aiogram.utils.exceptions
from InstanceBot import bot
from aiogram import types, Dispatcher
from database.db import db
from states import User
from keyboards import Keyboards


async def text(message: types.Message):
    user_id = message.from_user.id

    try:
        r = await bot.send_message(
            chat_id=user_id,
            text=message.text
        )
        await bot.delete_message(user_id, r.message_id)
    except Exception as e:
        print(e)
        await bot.send_message(
            chat_id=user_id,
            text='<b>Неверное заполнение HTML кода</b>'
        )
        return

    await db.update_mail_setting(text=message.text)

    await bot.send_message(
        chat_id=user_id,
        text='<b>📨 Настройка рассылки</b>',
        reply_markup=await Keyboards.mail_setting()
    )


async def mail_setting(call: types.CallbackQuery):
    user_id = call.from_user.id
    temp = call.data.split('|')

    if temp[1] == 'photo':
        if temp[2] == 'add':
            await User.admin_mail.photo.set()
            await bot.edit_message_text(
                chat_id=user_id,
                text='<b>Отправь фото для рассылки</b>',
                message_id=call.message.message_id
            )
        if temp[2] == 'info':
            mail = await db.get_info_mail()

            await bot.answer_callback_query(
                callback_query_id=call.id,
                text='✅'
            )

            await bot.send_photo(
                chat_id=user_id,
                photo=mail[2]
            )
        if temp[2] == 'del':
            await db.update_mail_setting(photo=True, delete=True)

            await bot.answer_callback_query(
                callback_query_id=call.id,
                text='✅'
            )

            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=await Keyboards.mail_setting()
            )
    if temp[1] == 'buttons':
        if temp[2] == 'add':
            await User.admin_mail.button.set()
            await bot.edit_message_text(
                chat_id=user_id,
                text='<b>Отправь кнопки для рассылки и их расположение:\n\n'
                     '1, 2, 3 (Ширина клавиатуры)\n'
                     'НАЗВАНИЕ|ССЫЛКА\n'
                     'НАЗВАНИЕ|ССЫЛКА\n'
                     'НАЗВАНИЕ|ССЫЛКА\n</b>',
                message_id=call.message.message_id
            )
        if temp[2] == 'info':
            mail = await db.get_info_mail()

            await bot.answer_callback_query(
                callback_query_id=call.id,
                text='✅'
            )

            await bot.send_message(
                chat_id=user_id,
                text='Клавиатура',
                reply_markup=await Keyboards.user_mail(mail[3].split('\n'))
            )
        if temp[2] == 'del':
            await db.update_mail_setting(buttons=True, delete=True)

            await bot.answer_callback_query(
                callback_query_id=call.id,
                text='✅'
            )

            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=await Keyboards.mail_setting()
            )
    if temp[1] == 'show':
        mail = await db.get_info_mail()

        await bot.answer_callback_query(
            callback_query_id=call.id,
            text='✅'
        )

        if mail[2]:
            if mail[3]:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=mail[2],
                    caption=mail[1],
                    reply_markup=await Keyboards.user_mail(mail[3].split('\n'))
                )
            else:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=mail[2],
                    caption=mail[1]
                )
        else:
            if mail[3]:
                await bot.send_message(
                    chat_id=user_id,
                    text=mail[1],
                    reply_markup=await Keyboards.user_mail(mail[3].split('\n'))
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=mail[1]
                )
    if temp[1] == 'run':
        mail = await db.get_info_mail()

        await bot.answer_callback_query(
            callback_query_id=call.id,
            text='Запускаю рассылку...'
        )

        count = 0
        count_accept = 0
        count_reject = 0
        for i in await db.get_users():

            await bot.edit_message_text(
                chat_id=user_id,
                text=f'<b>Рассылка запущена</b>\n\n'
                     f'<b>Прогресс:</b> {count} / {len(await db.get_users())}\n\n'
                     f'<b>Отправлено:</b> {count_accept}\n'
                     f'<b>Ошибок:</b> {count_reject}',
                message_id=call.message.message_id
            )

            try:
                if mail[2]:
                    if mail[3]:
                        await bot.send_photo(
                            chat_id=i[1],
                            photo=mail[2],
                            caption=mail[1],
                            reply_markup=await Keyboards.user_mail(mail[3].split('\n'))
                        )
                    else:
                        await bot.send_photo(
                            chat_id=i[1],
                            photo=mail[2],
                            caption=mail[1]
                        )
                else:
                    if mail[3]:
                        await bot.send_message(
                            chat_id=i[1],
                            text=mail[1],
                            reply_markup=await Keyboards.user_mail(mail[3].split('\n'))
                        )
                    else:
                        await bot.send_message(
                            chat_id=i[1],
                            text=mail[1]
                        )
                count_accept += 1
                count += 1
                await asyncio.sleep(0.25)
            except aiogram.exceptions.BotBlocked:
                count_reject += 1
                count += 1
                await asyncio.sleep(0.25)
                continue
            except aiogram.exceptions.RetryAfter as e:
                await asyncio.sleep(e.timeout)
                continue
            except Exception as e:
                print(e)
                count_reject += 1
                count += 1
                await asyncio.sleep(0.25)
                continue

        await db.update_mail_setting(delete=True)

        await User.admin.start.set()
        await bot.edit_message_text(
            chat_id=user_id,
            text=f'<b>✅ Рассылка закончена</b>\n\n'
                 f'<b>Прогресс:</b> {count} / {len(await db.get_users())}\n\n'
                 f'<b>Отправлено:</b> {count_accept}\n'
                 f'<b>Ошибок:</b> {count_reject}',
            message_id=call.message.message_id,
            reply_markup=Keyboards.admin()
        )
    if temp[1] == 'back':
        await db.update_mail_setting(delete=True)

        await User.admin.start.set()
        await bot.edit_message_text(
            chat_id=user_id,
            text='<b>⚙️ Админ меню</b>',
            message_id=call.message.message_id,
            reply_markup=Keyboards.admin()
        )


async def photo(message: types.Message):
    user_id = message.from_user.id

    await db.update_mail_setting(photo=message.photo[-1].file_id)

    await User.admin_mail.start.set()
    await bot.send_message(
        chat_id=user_id,
        text='<b>📨 Настройка рассылки</b>',
        reply_markup=await Keyboards.mail_setting()
    )


async def button(message: types.Message):
    user_id = message.from_user.id

    buttons = message.text.split('\n')

    if not buttons[0].isdigit():
        await message.answer('<b>Ширина клавиатуры указывается цифрой</b>')
        return

    try:
        r = await bot.send_message(
            chat_id=user_id,
            text='Клавиатура',
            reply_markup=await Keyboards.user_mail(buttons)
        )
        await bot.delete_message(user_id, r.message_id)
    except Exception as e:
        print(e)
        await message.answer('<b>Неверное заполнение списка</b>')
        return

    await db.update_mail_setting(buttons=message.text)

    await User.admin_mail.start.set()
    await bot.send_message(
        chat_id=user_id,
        text='<b>📨 Настройка рассылки</b>',
        reply_markup=await Keyboards.mail_setting()
    )


def hand_add(dp: Dispatcher):
    dp.register_message_handler(text, content_types=['text'], state=User.admin_mail.start)

    dp.register_callback_query_handler(mail_setting, lambda c: c.data and c.data.startswith('t'),
                                       state=User.admin_mail.start)

    dp.register_message_handler(photo, content_types=['photo'], state=User.admin_mail.photo)
    dp.register_message_handler(button, content_types=['text'], state=User.admin_mail.button)
