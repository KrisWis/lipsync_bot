from .CheckSub import Sub
from aiogram.dispatcher import Dispatcher


def setup(dp: Dispatcher):
    dp.filters_factory.bind(Sub)
