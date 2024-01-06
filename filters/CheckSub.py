import datetime
# BoundFilter - это специальный класс в AIOGram для создания своих фильтров.
from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from database.db import db
from utils import payment, text
from keyboards import Keyboards

# Создаём собственный фильтр на проверку подписки
class Sub(BoundFilter):
    def __init__(self, yes_sub):
        self.yes_sub = yes_sub

    async def check(self, message: types.Message):
        user_id = message.from_user.id

        user = eval(db.get_info_user(user_id)[8])

        if user['tariff']['id'] == 0:
            return self.yes_sub

        now = datetime.datetime.now()

        if user['tariff']['date'] > now.strftime('%Y-%m-%d %H:%M'):
            return self.yes_sub

        else:
            user['tariff']['id'] = 0
            user['tariff']['name'] = payment.pay_tariffs[0]['name']
            user['tariff']['date'] = None
            user['tariff']['limits']['gpt35']['day'] = payment.pay_tariffs[0]['limits']['gpt35']['day']
            user['tariff']['limits']['gpt4']['month'] = payment.pay_tariffs[0]['limits']['gpt4']['month']
            user['tariff']['limits']['image']['month'] = payment.pay_tariffs[0]['limits']['image']['month']
            user['max_tokens'] = payment.pay_tariffs[0]['limits']['max_tokens']

            db.update_user(user_id, user_setting=user)

            await message.answer(
                text=text.timeout_sub,
                reply_markup=Keyboards.premium()
            )
            return False
