import asyncio
import datetime
import sys
import Config
from InstanceBot import bot
from aiohttp import ClientSession
from database.db import db
from elevenlabs import generate, clone, set_api_key
import traceback

# Обозначаем все функции для планировщика
# async def get_video_url(file_id, file_name):
#     try:
#         get = await bot.get_file(file_id)
#         url = bot.get_file_url(get.file_path)

#         print(url)

#         async with ClientSession() as s:
#             headers = {
#                 'Accept': 'application/json'
#             }
#             try:
#                 # with open('./1.mp4', 'rb') as bites:
#                 url = f'https://linx.sny.sh/upload/{file_name}'
#                 async with s.put(url=url, headers=headers, data=bites) as res:
#                     res = await res.json()

#                     return res['direct_url']

#             except Exception as e:
#                 await bot.send_message(
#                     chat_id=Config.admins[0],
#                     text=f'Ошибка ФО: {e}'
#                 )
#                 return None
#     except Exception as e:
#         await bot.send_message(
#             chat_id=Config.admins[0],
#             text=f'Ошибка download: {e}'
#         )
#         return None


async def split_audio(video_url, user_id):
    try:
        async with ClientSession() as s:
            json = {
                'apikey': Config.convertio,
                'input': 'url',
                'file': video_url,
                'outputformat': 'mp3'
            }
            url = 'https://api.convertio.co/convert'
            async with s.post(url=url, json=json) as res:
                res = await res.json()

                if res['status'] != 'ok':
                    raise Exception('Смените токен Convert Io!')

            url = f'http://api.convertio.co/convert/{res["data"]["id"]}/status'
            while res['data'].get('step', 'convert') == 'convert':
                async with s.get(url=url) as res_:
                    res = await res_.json()

                await asyncio.sleep(5)

            file_name = f"./users/{user_id}{res['data']['output']['url'].split('/')[-1]}"

            async with s.get(res['data']['output']['url']) as res:
                with open(file_name, 'wb') as audio:
                    audio.write(await res.read())

                return file_name

    except Exception as e:
        traceback.print_exc()
        await bot.send_message(
            chat_id=Config.admins[0],
            text=f'Ошибка Convert IO: {e}'
        )
        return None


async def generate_audio(text, audio):
    try:
        set_api_key(Config.elevenlabs)

        voice = clone(
            name=audio.split('/')[-1],
            files=[audio]
        )

        new_voice = generate(
            text=text,
            voice=voice,
            model='eleven_multilingual_v2'
        )

        async with ClientSession() as s:
            headers = {
                'Accept': 'application/json'
            }
            url = f'https://linx.sny.sh/upload/{audio.split("/")[-1]}'
            try:
                async with s.put(url=url, headers=headers, data=new_voice) as res:
                    res = await res.json()

                    return res['direct_url']

            except Exception as e:
                traceback.print_exc()
                await bot.send_message(
                    chat_id=Config.admins[0],
                    text=f'Ошибка ФО: {e}'
                )
                return None

    except Exception as e:
        traceback.print_exc()
        await bot.send_message(
            chat_id=Config.admins[0],
            text=f'Ошибка Elevenlabs: {e}'
        )
        return None


async def generate_video(video_url, voice_url):
    try:
        async with ClientSession() as s:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'x-api-key': Config.sync_lab
            }
            json = {
                'audioUrl': voice_url,
                'videoUrl': video_url,
                'synergize': True,
                'maxCredits': None,
                'webhookUrl': None,
            }
            url = 'https://api.synclabs.so/video'

            async with s.post(url=url, headers=headers, json=json) as res:
                res = await res.json()

                print(res)
                #if res['status'] == 401:
                    #raise Exception('Сменить API-KEY у Sync Labs')

            url = f'https://api.synclabs.so/video/{res["id"]}'
            while res['status'] == 'PENDING' or res['status'] == 'PROCESSING':
                async with s.get(url=url, headers=headers) as res:
                    res = await res.json()

                    if res['status'] == 'FAILED':
                        return None

                await asyncio.sleep(5)

            return res['url'] if res['url'] != '' else None

    except Exception as e:
        traceback.print_exc()
        await bot.send_message(
            chat_id=Config.admins[0],
            text=f'Ошибка Sync labs: {e.with_traceback(tb=sys.exc_info(e)[2])}'
        )
        return None


# Функция для обновления запросов оплаты на дефолт (юзер всё оплатил, поэтому возвращаем к изначальному состоянию)
async def update_requests():
    for i in await db.get_users():

        user = await db.get_info_user(i[1])

        if not user[10]:
            continue

        now = datetime.datetime.date()

        if user[10] >= now:
            continue

        else:
            await db.update_paid_status(
                user_id=user[1],
                paid_type='Free',
                paid_date=None,
                requests=0
            )
