from aiogram.dispatcher.filters.state import State, StatesGroup


class menu(StatesGroup):
    video = State()
    text = State()


class admin(StatesGroup):
    start = State()
    stata = State()


class admin_mail(StatesGroup):
    start = State()
    choice = State()

    photo = State()
    button = State()
    run = State()


class admin_channels(StatesGroup):
    start = State()
    add = State()
    delete = State()
