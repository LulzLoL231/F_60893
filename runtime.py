# -*- coding: utf-8 -*-
#
#  F_60893 - runtime vars & funcs.
#  Created by LulzLoL231 at 10/6/21
#
from logging import getLogger
from asyncio import get_event_loop

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import i18n
from config import config
from database import Database


cmds = [
    BotCommand('start', 'Запустить бота')
]

getLogger(config.NAME).info(f'Telegram Bot {config.NAME} v{config.VERSION}')
loop = get_event_loop()
bot = Dispatcher(
    Bot(config.getToken(), loop, parse_mode='HTML'),
    loop,
    storage=MemoryStorage()
)
langs = i18n.Languages()
db = Database()
loop.run_until_complete(db.check_database())
loop.run_until_complete(bot.bot.set_my_commands(cmds))
bot_user = loop.run_until_complete(bot.bot.get_me())
