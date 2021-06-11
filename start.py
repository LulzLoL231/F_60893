# -*- coding: utf-8 -*-
#
#  F_60893 - startup script.
#  Created by LulzLoL231 at 10/6/21
#
from aiogram.utils.executor import start_polling


import cmds
from runtime import bot
from config import config


if __name__ == '__main__':
    start_polling(bot)
