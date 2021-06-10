# -*- coding: utf-8 -*-
#
#  F_60893 - runtime vars & funcs.
#  Created by LulzLoL231 at 10/6/21
#
from asyncio import get_event_loop
from typing import Any, Dict, List

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import storage
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import i18n
from config import config


cmds = [
    BotCommand('start', 'Start'),
    BotCommand('help', 'Help page'),
    BotCommand('version', 'Bot version')
]


loop = get_event_loop()
bot = Dispatcher(
    Bot(config.getToken(), loop, parse_mode='HTML'),
    loop,
    storage=MemoryStorage()
)
langs = i18n.Languages()
db: Dict[str, Dict[int, Dict[str, Any]]] = {
    'users': {}
}
loop.run_until_complete(bot.bot.set_my_commands(cmds))
