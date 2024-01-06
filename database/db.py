from datetime import datetime, timedelta
import Config
# Union нужен для типизации в Python
from typing import Union
import asyncpg
from asyncpg import Connection
""" Для приложений серверного типа, которые обрабатывают частые запросы и 
которым требуется подключение к базе данных на короткий период времени при обработке запроса, рекомендуется использовать пул подключений. """
from asyncpg.pool import Pool


# Определеяем класс базы данных
class Database:
    def __init__(self):
        # Объявляем наш пул
        self.pool: Union[Pool, None] = None

    async def create_pool(self):
        # Создаём пул
        self.pool = await asyncpg.create_pool(**Config.pg)

    # Функция для получения списка всех строк, подходящих по условию
    async def fetch(self, sql, *args):
        # acquire() делает подключение из пула
        async with self.pool.acquire() as connection:
            connection: Connection

            # Делаем саму операцию подключения
            async with connection.transaction():
                # И через подключение осуществляем вводимый запрос.
                res = await connection.fetch(sql, *args)

            return res

    # Функция для получения количества строк
    async def fetchval(self, sql, *args):
        async with self.pool.acquire() as connection:
            connection: Connection

            async with connection.transaction():
                res = await connection.fetchval(sql, *args)

            return res

    # Функция для получения одной строки, подходящей по условию
    async def fetchrow(self, sql, *args):
        async with self.pool.acquire() as connection:
            connection: Connection

            async with connection.transaction():
                res = await connection.fetchrow(sql, *args)

            return res

    # Функция для методов "INSERT, DELETE, UPDATE, CREATE".
    async def execute(self, sql, *args):
        async with self.pool.acquire() as connection:
            connection: Connection

            async with connection.transaction():
                res = await connection.execute(sql, *args)

            return res

    # Функция для создания таблиц
    async def create_tables(self):
        await self.execute('''CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            user_id BIGINT NOT NULL,
                            username TEXT,
                            date DATE NOT NULL,
                            premium BOOLEAN,
                            walk_op BOOLEAN,
                            active BOOLEAN,
                            geo TEXT NOT NULL,
                            tag TEXT,
                            paid_type TEXT,
                            paid_date DATE,
                            requests BIGINT DEFAULT (0),
                            requests_buy BIGINT DEFAULT (0))
                            ''')
        print('Юзеры запущены')

        await self.execute('''CREATE TABLE IF NOT EXISTS settings (
                            id SERIAL PRIMARY KEY,
                            amount BIGINT DEFAULT (0))
                            ''')
        print('Настройки запущены')

        await self.execute('''CREATE TABLE IF NOT EXISTS mail_setting (
                            id SERIAL PRIMARY KEY,
                            text TEXT,
                            photo TEXT,
                            buttons TEXT);
                            ''')
        print('Настройки рассылки запущены')


    @staticmethod
    def format_args(sql, parameters: dict):
        sql += ' AND '.join([f'{i} = ${a}' for i, a in enumerate(parameters.keys(), start=1)])
        return sql, tuple(parameters.values())

    async def user_exists(self, user_id):
        sql = 'SELECT user_id FROM users WHERE user_id = $1'

        if not await self.fetchrow(sql, user_id):
            return False

        return True

    async def add_user(self, user_id, username, date, premium, geo, tag):
        sql = '''INSERT INTO users (user_id, username, date, premium, walk_op, active, geo, tag, paid_type, paid_date) 
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)'''
        await self.execute(sql, user_id, username, date, premium, False, False, geo, tag, 'Free', None)

    async def get_info_user(self, user_id):
        sql = 'SELECT * FROM users WHERE user_id = $1'
        return await self.fetchrow(sql, user_id)

    async def update_user(self, user_id, premium=None, walk_op=None, active=None):
        if premium:
            sql = 'UPDATE users SET premium = $1 WHERE user_id = $2'
            await self.execute(sql, premium, user_id)

        if walk_op:
            sql = 'UPDATE users SET walk_op = $1 WHERE user_id = $2'
            await self.execute(sql, walk_op, user_id)

        if active:
            sql = 'UPDATE users SET active = $1 WHERE user_id = $2'
            await self.execute(sql, active, user_id)

    async def update_paid_status(self, user_id, paid_type=None, paid_date=None, requests: int = None):
        if paid_type:
            sql = 'UPDATE users SET paid_type = $1, paid_date = $2, requests = $3  WHERE user_id = $4'
            await self.execute(sql, paid_type, paid_date, requests, user_id)

        else:
            sql = 'UPDATE users SET requests_buy = requests_buy + $1  WHERE user_id = $2'
            await self.execute(sql, requests, user_id)

    async def update_requests(self, user_id, buy=None):
        if not buy:
            sql = 'UPDATE users SET requests = requests - 1 WHERE user_id = $1'
            await self.execute(sql, user_id)

        else:
            sql = 'UPDATE users SET requests_buy = requests_buy - 1 WHERE user_id = $1'
            await self.execute(sql, user_id)

    async def get_users(self, period=None, premium=None, walk_op=None,
                        active=None, geo=None, tag=None):
        now = datetime.now()
        date = now
        all_stat = None

        if not period:
            all_stat = True

        if period == 'day':
            date = now

        if period == 'week':
            week = now - timedelta(weeks=1)
            date = week

        if period == 'month':
            month = now - timedelta(days=30)
            date = month

        if premium:
            if not all_stat:
                sql = '''SELECT * FROM users 
                          WHERE date >= $1
                          AND premium = $2'''
                return len(await self.fetch(sql, date, premium))
            else:
                sql = 'SELECT * FROM users WHERE premium = $1'
                return len(await self.fetch(sql, premium))

        elif walk_op:
            if not all_stat:
                sql = '''SELECT * FROM users 
                          WHERE date >= $1
                          AND walk_op = $2'''
                return len(await self.fetch(sql, date, walk_op))
            else:
                sql = 'SELECT * FROM users WHERE walk_op = $1'
                return len(await self.fetch(sql, walk_op))

        elif active:
            if not all_stat:
                sql = '''SELECT * FROM users 
                          WHERE date >= $1
                          AND active = $2'''
                return len(await self.fetch(sql, date, active))
            else:
                sql = 'SELECT * FROM users WHERE active = $1'
                return len(await self.fetch(sql, active))

        elif geo:
            if not all_stat:
                # DISTINCT используется для того, чтобы брать только различные значения.
                sql = '''SELECT DISTINCT geo, COUNT(user_id) AS count FROM users 
                          WHERE date >= $1
                          GROUP BY geo
                          ORDER BY count DESC
                          LIMIT 10'''

                name = await self.fetch(sql, date)

                count_geo = {}
                for country in name:
                    count_geo[country[0]] = int(country[1])

                msg = ''
                for i in count_geo:
                    msg += f'{i}: {count_geo[i]} ' \
                           f'({round(count_geo[i] / await self.get_users(period=period) * 100, 2)}%)\n'

                return msg
            else:
                sql = '''SELECT DISTINCT geo, COUNT(user_id) AS count FROM users 
                          GROUP BY geo
                          ORDER BY count DESC'''

                name = await self.fetch(sql)

                count_geo = {}
                for country in name:
                    count_geo[country[0]] = int(country[1])

                msg = ''
                for i in count_geo:
                    msg += f'{i}: {count_geo[i]} ({round(count_geo[i] / len(await self.get_users()) * 100, 2)}%)\n'

                return msg

        elif tag:
            if not all_stat:
                sql = '''SELECT DISTINCT tag, COUNT(user_id) AS count FROM users 
                          WHERE date >= $1
                          GROUP BY tag
                          ORDER BY count DESC
                          LIMIT 10'''

                name = await self.fetch(sql, date)

                tags = {}
                for tag in name:
                    tags[tag[0]] = int(tag[1])

                msg = ''
                for i in tags:
                    msg += f'{i}: {tags[i]} ({round(tags[i] / await self.get_users(period=period) * 100, 2)}%)\n'

                return msg

            else:
                sql = '''SELECT DISTINCT tag, COUNT(user_id) AS count FROM users 
                          GROUP BY tag
                          ORDER BY count DESC;'''

                name = await self.fetch(sql)

                tags = {}
                for tag in name:
                    tags[tag[0]] = int(tag[1])

                msg = ''
                for i in tags:
                    msg += f'{i}: {tags[i]} ({round(tags[i] / len(await self.get_users()) * 100, 2)}%)\n'

                return msg

        else:
            if not all_stat:
                sql = 'SELECT * FROM users WHERE date >= $1;'
                return len(await self.fetch(sql, date))
            else:
                sql = 'SELECT * FROM users'
                return await self.fetch(sql)

    async def get_tag_stata(self, tag=None, premium=None, walk_op=None, active=None, all_stat=None):
        if tag:
            temp_msg = []

            if all_stat:
                sql = '''SELECT DISTINCT tag, COUNT(user_id) AS count FROM users
                          WHERE tag IS NOT NULL
                          GROUP BY tag
                          ORDER BY count DESC'''

                all_stat = await self.fetch(sql)

                msg = '<b>Общий заход:</b>\n'
                for i in all_stat:
                    msg += f'{i[0]}: {i[1]}\n'
                msg += '\n'

                temp_msg.append(msg)

            if premium:
                sql = '''SELECT DISTINCT tag, COUNT(user_id) AS count FROM users 
                          WHERE premium = $1
                          AND tag IS NOT NULL
                          GROUP BY tag
                          ORDER BY count DESC'''

                prem = await self.fetch(sql, premium)

                msg = '<b>Премиум пользователи:</b>\n'
                for i in prem:
                    msg += f'{i[0]}: {i[1]}\n'
                msg += '\n'

                temp_msg.append(msg)
            if walk_op:
                sql = '''SELECT DISTINCT tag, COUNT(user_id) AS count FROM users 
                          WHERE walk_op = $1
                          AND tag IS NOT NULL
                          GROUP BY tag
                          ORDER BY count DESC
                          LIMIT 10'''

                walk = await self.fetch(sql, walk_op)

                msg = '<b>Прошли ОП:</b>\n'
                for i in walk:
                    msg += f'{i[0]}: {i[1]}\n'
                msg += '\n'

                temp_msg.append(msg)

            if active:
                sql = '''SELECT DISTINCT tag, COUNT(user_id) AS count FROM users 
                                  WHERE active = $1
                                  AND tag IS NOT NULL
                                  GROUP BY tag
                                  ORDER BY count DESC
                                  LIMIT 10'''

                active = await self.fetch(sql, active)

                msg = '<b>Активные:</b>\n'
                for i in active:
                    msg += f'{i[0]}: {i[1]}\n'
                msg += '\n'

                temp_msg.append(msg)

            finish = '<b>Статистика по тегам:</b>\n\n'
            for i in temp_msg:
                finish += i

            return finish

    async def update_mail_setting(self, text=None, photo=None, buttons=None, delete=None):
        if text:
            sql = 'UPDATE mail_setting SET text = $1 WHERE id = 1'
            await self.execute(sql, text)

        if photo:
            sql = 'UPDATE mail_setting SET photo = $1 WHERE id = 1'
            await self.execute(sql, photo)

        if buttons:
            sql = 'UPDATE mail_setting SET buttons = $1 WHERE id = 1'
            await self.execute(sql, buttons)

        if delete:
            if text:
                sql = 'UPDATE mail_setting SET text = $1 WHERE id = 1'
                await self.execute(sql, None)

            elif photo:
                sql = 'UPDATE mail_setting SET photo = $1 WHERE id = 1'
                await self.execute(sql, None)

            elif buttons:
                sql = 'UPDATE mail_setting SET buttons = $1 WHERE id = 1'
                await self.execute(sql, None)

            else:
                sql1 = 'UPDATE mail_setting SET text = $1 WHERE id = 1'
                await self.execute(sql1, None)
                sql2 = 'UPDATE mail_setting SET photo = $1 WHERE id = 1'
                await self.execute(sql2, None)
                sql3 = 'UPDATE mail_setting SET buttons = $1 WHERE id = 1'
                await self.execute(sql3, None)

    async def get_info_mail(self):
        sql = 'SELECT * FROM mail_setting'
        return await self.fetchrow(sql)


db = Database()
