# Бот для создания липсинков
#### Бот создан по техническому задания заказчика, но так же для практики работы с различными API (в боте использованы elevenlabs, convertio и SyncLab).

# Запуск бота
Инструкция, чтобы запустить собственного бота:
   1. Установите Python.
   2. Склонируйте данный репозиторий.
   3. Установите необходимые библиотеки и модули.
   4. В файле ```Config.py``` введите свой токен телеграмм бота в переменной ```TOKEN```, а также токен крипто бота в переменной ```CRYPTO_BOT_TOKEN```.
   5. В том же файле конфига, в переменной ```pg```, в поле password и database введите соответственно пароль и название своей базы данных.
   6. После этого, в переменных ```convertio```, ```elevenlabs``` и ```sync_lab``` введите ваши API ключи от данных сервисов.
   7. В массиве ```admins``` в формате числа введите Telegram ID пользователей, которые будут администраторами.
   8. Создайте Telegram-бота у [BotFather](https://t.me/deepface_testing_bot).
   9. Запустите бота, написав в терминал: ```python RunBot.py```

Или, вы можете воспользоваться ботом по [ссылке](https://t.me/tagnumber_bot).
