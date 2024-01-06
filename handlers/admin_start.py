import aiogram
from InstanceBot import bot
from aiogram import types, Dispatcher
from database.db import db
from states import User
from keyboards import Keyboards


async def admin(call: types.CallbackQuery):
    user_id = call.from_user.id
    temp = call.data.split('|')

    if temp[1] == 'stata':
        await bot.answer_callback_query(
            callback_query_id=call.id,
            text='✅'
        )

        await User.admin.stata.set()
        await bot.edit_message_text(
            chat_id=user_id,
            text=f'<b>Статистика</b>',
            message_id=call.message.message_id,
            reply_markup=await Keyboards.admin_stata()
        )

    if temp[1] == 'mail':
        await User.admin_mail.start.set()
        await bot.edit_message_text(
            chat_id=user_id,
            text='<b>📨 Введите текст для рассылки, HTML</b>',
            message_id=call.message.message_id
        )


async def stata(call: types.CallbackQuery):
    user_id = call.from_user.id
    temp = call.data.split('|')

    await bot.answer_callback_query(
        callback_query_id=call.id
    )

    if temp[1] == 'day':
        try:
            await bot.edit_message_text(
                chat_id=user_id,
                text=f'<b>📊 Статистика за день</b>\n\n'
                     f'<b>👤 Пользователи:</b>\n'
                     f'<b>Всего:</b> {await db.get_users(period=temp[1])}\n'
                     f'<b>Прем</b>: {await db.get_users(period=temp[1], premium=True)} '
                     f'({round(await db.get_users(period=temp[1], premium=True) / await db.get_users(period=temp[1]) * 100, 2)}%)\n'
                     f'<b>Прошли ОП:</b> {await db.get_users(period=temp[1], walk_op=True)} '
                     f'({round(await db.get_users(period=temp[1], walk_op=True) / await db.get_users(period=temp[1]) * 100, 2)}%)\n'
                     f'<b>Актив:</b> {await db.get_users(period=temp[1], active=True)} '
                     f'({round(await db.get_users(period=temp[1], active=True) / await db.get_users(period=temp[1]) * 100, 2)}%)\n\n'
                     f'<b>🌎 ГЕО:</b>\n'
                     f'{await db.get_users(period=temp[1], geo=True)}\n\n'
                     f'<b>📈 ТРАФИК:</b>\n'
                     f'{await db.get_users(period=temp[1], tag=True)}',
                message_id=call.message.message_id,
                reply_markup=await Keyboards.admin_stata()
            )
        except aiogram.exceptions.MessageNotModified:
            pass

    if temp[1] == 'week':
        try:
            await bot.edit_message_text(
                chat_id=user_id,
                text=f'<b>📊 Статистика за неделю</b>\n\n'
                     f'<b>👤 Пользователи:</b>\n'
                     f'<b>Всего:</b> {await db.get_users(period=temp[1])}\n'
                     f'<b>Прем</b>: {await db.get_users(period=temp[1], premium=True)} '
                     f'({round(await db.get_users(period=temp[1], premium=True) / await db.get_users(period=temp[1]) * 100, 2)}%)\n'
                     f'<b>Прошли ОП:</b> {await db.get_users(period=temp[1], walk_op=True)} '
                     f'({round(await db.get_users(period=temp[1], walk_op=True) / await db.get_users(period=temp[1]) * 100, 2)}%)\n'
                     f'<b>Актив:</b> {await db.get_users(period=temp[1], active=True)} '
                     f'({round(await db.get_users(period=temp[1], active=True) / await db.get_users(period=temp[1]) * 100, 2)}%)\n\n'
                     f'<b>🌎 ГЕО:</b>\n'
                     f'{await db.get_users(period=temp[1], geo=True)}\n\n'
                     f'<b>📈 ТРАФИК:</b>\n'
                     f'{await db.get_users(period=temp[1], tag=True)}',
                message_id=call.message.message_id,
                reply_markup=await Keyboards.admin_stata()
            )
        except aiogram.exceptions.MessageNotModified:
            pass

    if temp[1] == 'month':
        try:
            await bot.edit_message_text(
                chat_id=user_id,
                text=f'<b>📊 Статистика за месяц</b>\n\n'
                     f'<b>👤 Пользователи:</b>\n'
                     f'<b>Всего:</b> {await db.get_users(period=temp[1])}\n'
                     f'<b>Прем</b>: {await db.get_users(period=temp[1], premium=True)} '
                     f'({round(await db.get_users(period=temp[1], premium=True) / await db.get_users(period=temp[1]) * 100, 2)}%)\n'
                     f'<b>Прошли ОП:</b> {await db.get_users(period=temp[1], walk_op=True)} '
                     f'({round(await db.get_users(period=temp[1], walk_op=True) / await db.get_users(period=temp[1]) * 100, 2)}%)\n'
                     f'<b>Актив:</b> {await db.get_users(period=temp[1], active=True)} '
                     f'({round(await db.get_users(period=temp[1], active=True) / await db.get_users(period=temp[1]) * 100, 2)}%)\n\n'
                     f'<b>🌎 ГЕО:</b>\n'
                     f'{await db.get_users(period=temp[1], geo=True)}\n\n'
                     f'<b>📈 ТРАФИК:</b>\n'
                     f'{await db.get_users(period=temp[1], tag=True)}',
                message_id=call.message.message_id,
                reply_markup=await Keyboards.admin_stata()
            )
        except aiogram.exceptions.MessageNotModified:
            pass

    if temp[1] == 'all':
        try:
            await bot.edit_message_text(
                chat_id=user_id,
                text=f'<b>📊 Статистика за все время</b>\n\n'
                     f'<b>👤 Пользователи:</b>\n'
                     f'<b>Всего:</b> {len(await db.get_users())}\n'
                     f'<b>Прем</b>: {await db.get_users(premium=True)} '
                     f'({round(await db.get_users(premium=True) / len(await db.get_users()) * 100, 2)}%)\n'
                     f'<b>Прошли ОП:</b> {await db.get_users(walk_op=True)} '
                     f'({round(await db.get_users(walk_op=True) / len(await db.get_users()) * 100, 2)}%)\n'
                     f'<b>Актив:</b> {await db.get_users(active=True)} '
                     f'({round(await db.get_users(active=True) / len(await db.get_users()) * 100, 2)}%)\n\n'
                     f'<b>🌎 ГЕО:</b>\n'
                     f'{await db.get_users(geo=True)}\n\n'
                     f'<b>📈 ТРАФИК:</b>\n'
                     f'{await db.get_users(tag=True)}',
                message_id=call.message.message_id,
                reply_markup=await Keyboards.admin_stata()
            )
        except aiogram.exceptions.MessageNotModified:
            pass

    if temp[1] == 'back':
        await User.admin.start.set()
        await bot.edit_message_text(
            chat_id=user_id,
            text='<b>⚙️ Админ меню</b>',
            message_id=call.message.message_id,
            reply_markup=await Keyboards.admin()
        )


def hand_add(dp: Dispatcher):
    dp.register_callback_query_handler(admin, lambda c: c.data and c.data.startswith('a'), state=User.admin.start)
    dp.register_callback_query_handler(stata, lambda c: c.data and c.data.startswith('x'), state=User.admin.stata)
