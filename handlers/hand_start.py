import datetime
import os
import aiogram
import traceback
import Config
from InstanceBot import bot
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from database.db import db
from keyboards import Keyboards
from states import User
from utils import text, scheduler


async def start(message: types.Message):
    user_id = message.from_user.id
    now = datetime.datetime.now()

    if not await db.user_exists(user_id):
        start_tag = message.text[7:]

        if len(start_tag) != 0:
            if start_tag.isdigit() and start_tag != str(user_id):
                start_tag = start_tag
        else:
            start_tag = 'Органика'

        await db.add_user(
            user_id,
            message.from_user.username,
            now,
            message.from_user.is_premium,
            message.from_user.language_code,
            start_tag
        )

    try:
        await message.answer_video(
            video='BAACAgIAAxkBAAMDZY6CrQpy35PhQDpQkKAUlJqQGtcAAsg5AAKBDklI26abArMnA1c0BA'
        )
        await message.answer(text.start_text, reply_markup=Keyboards.start_message())

    except aiogram.exceptions.RetryAfter:
        pass


async def commands(message: types.Message):
    user_id = message.from_user.id

    if message.text == '/premium':
        await message.answer(
            text=text.premium_text,
            reply_markup=Keyboards.premium()
        )

    if message.text == '/create_video':
        user = await db.get_info_user(user_id)

        if not user[10] and user[11] + user[12] == 0:
            await message.answer(
                text=text.none_premium,
                reply=True,
                reply_markup=Keyboards.premium()
            )
            return
        
        await message.answer_video(
            video='BAACAgIAAxkBAAMFZY6DFJVcmzNfDRLn4w-EkUaOyMkAAu05AAKBDklIAAGu2EG1oXgZNAQ',
            caption=text.help_text
        )
        
        await message.answer(
            text=text.get_video
        )

        await User.menu.video.set()

    if message.text == '/account':
        user = await db.get_info_user(user_id)

        await message.answer(
            text=text.account_text.format(
                user_id,
                user[11] + user[12],
                '✅' if user[10] else '❌',
                user[10] if user[10] else '❌',
            )
        )

    if message.text == '/admin':
        if user_id in Config.admins:
            await User.admin.start.set()
            await message.answer(
                text='Админ меню',
                reply_markup=Keyboards.admin()
            )

    if message.text == '/help':
        await message.answer_video(
            video='BAACAgIAAxkBAAMFZY6DFJVcmzNfDRLn4w-EkUaOyMkAAu05AAKBDklIAAGu2EG1oXgZNAQ',
            caption=text.help_text
        )
        

async def get_video(message: types.Message, state: FSMContext):

    try:
        user_id = message.from_user.id

        if message.video.duration > 300:
            await message.answer(
                text=text.error_duration
            )
            return

        r = await message.answer(
            text=text.process[1]
        )

        # video_url = await scheduler.get_video_url(message.video.file_id, message.video.file_name)
        # ЭТО НЕ УДАЛЯЙ, ПУСТЬ БУДЕТ
        # if not video_url:
        #     await bot.delete_message(user_id, r.message_id)
        #
        #     await state.finish()
        #     await message.answer(
        #         text=text.error_generate
        #     )
        #     return

        get = await bot.get_file(message.video.file_id)
        video_url = bot.get_file_url(get.file_path)

        await bot.edit_message_text(
            chat_id=message.from_user.id,
            text=text.process[2],
            message_id=r.message_id
        )

        split_audio = await scheduler.split_audio(video_url, message.from_user.id)

        if not split_audio:
            await bot.delete_message(user_id, r.message_id)

            await state.finish()
            await message.answer(
                text=text.error_generate
            )
            return

        async with state.proxy() as data:
            data['video_url'] = video_url
            data['split_audio'] = split_audio

        await bot.delete_message(user_id, r.message_id)

        await User.menu.text.set()
        await message.answer(
            text=text.get_text
        )

    except:
        traceback.print_exc()
        await bot.delete_message(user_id, r.message_id)

        await state.finish()
        await message.answer(
            text=text.error_generate
        )
        return

async def get_text(message: types.Message, state: FSMContext):

    try:
        user_id = message.from_user.id

        async with state.proxy() as data:
            video_url = data['video_url']
            split_audio = data['split_audio']

        r = await message.answer(
            text=text.process[3]
        )

        new_voice = await scheduler.generate_audio(message.text, split_audio)

        if not new_voice:
            await bot.delete_message(user_id, r.message_id)

            os.remove(split_audio)

            await state.finish()
            await message.answer(
                text=text.error_generate
            )
            return

        await bot.edit_message_text(
            chat_id=message.from_user.id,
            text=text.process[4],
            message_id=r.message_id
        )

        new_video = await scheduler.generate_video(video_url, new_voice)

        if not new_video:
            await bot.delete_message(user_id, r.message_id)

            os.remove(split_audio)

            await state.finish()
            await message.answer(
                text=text.error_generate
            )
            return

        os.remove(split_audio)

        await bot.delete_message(user_id, r.message_id)

        user = await db.get_info_user(user_id)

        if user[11] > 0 and user[12] == 0:
            await db.update_requests(user_id)

        elif user[11] == 0 and user[12] > 0:
            await db.update_requests(user_id, buy=True)

        else:
            await db.update_requests(user_id)

        await state.finish()
        await message.answer_video(
            video=new_video,
            caption=text.process[5]
        )

        await message.answer_video(
            video='BAACAgIAAxkBAAMHZY6DNLpHx7brbTx7kX0X21cKtR0AAthHAAJREmhItWGwnjg_GWE0BA'
        )

        await message.answer_video(
            video='BAACAgIAAxkBAAMJZY6DOfQPstymEOjxFh1erUYcxXUAAi1JAALKl3BICBk9ancvPoQ0BA'
        )

        await message.answer_video(
            video='BAACAgIAAxkBAAMLZY6DP8YrVhXDcx7iORLz95-R-XYAAjFJAALKl3BITDhlXvTDroQ0BA',
            reply_markup=Keyboards.offer_new_kb()
        )

    except: 
        traceback.print_exc()
        await state.finish()
        await message.answer(
            text=text.error_generate
        )
        return

async def get_file_id(message: types.Message):
    if message.from_user.id in Config.admins:
        await message.answer(message.video.file_id)


async def start_callback(call: types.CallbackQuery):
    await call.message.answer(
            text=text.premium_text,
            reply_markup=Keyboards.premium()
        )
    

async def create_video_callback(call: types.CallbackQuery):
    user = await db.get_info_user(call.from_user.id)

    if not user[10] and user[11] + user[12] == 0:
        await call.message.answer(
            text=text.none_premium,
            reply=True,
            reply_markup=Keyboards.premium()
        )
        return
    
    await call.message.answer_video(
        video='BAACAgIAAxkBAAMFZY6DFJVcmzNfDRLn4w-EkUaOyMkAAu05AAKBDklIAAGu2EG1oXgZNAQ',
        caption=text.help_text
    )
    
    await call.message.answer(
        text=text.get_video
    )

    await User.menu.video.set()


def hand_add(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_message_handler(commands, commands=['premium', 'create_video', 'help', 'account', 'admin'], state='*')
    dp.register_message_handler(get_video, content_types=['video'], state=User.menu.video)
    dp.register_message_handler(get_text, content_types=['text'], state=User.menu.text)
    dp.register_callback_query_handler(start_callback, lambda c: c.data == "start_premium", state='*')
    dp.register_callback_query_handler(create_video_callback, lambda c: c.data == "success_payment",  state='*')
    #dp.register_message_handler(get_file_id, content_types=['video'], state='*')
