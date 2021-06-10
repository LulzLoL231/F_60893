# -*- coding: utf-8 -*-
#
#  F_60893 - configuration.
#  Created by LulzLoL231 at 10/6/21
#
import logging
from os import environ
from datetime import datetime


BOT_NAME = 'F_60893'
VERSION = '0.0.1'
USR_TEMP = {
    'uid': 0,
    'registered': False,
    'premium': False,
    'premium_start': datetime.max,
    'premium_end': datetime.min,
    'lang': ''
}


class Configuration:
    '''Конфигурация бота.

    Args:
        DEBUG (bool) - Дебаг режим. Стандарт: False.
        DEV (bool) - Режим разработчика. Стандарт: False.
        TOKEN (str) - Основной токен бота. Стандарт: "UNKNOWN".
        TEST_TOKEN (str) - Тестовый токен бота. Стандарт: "UNKNOWN".
        ADMIN_ID (int) - Telegram userID администратора. Стандарт: 0.
        DEFAULT_LANG (str) - Стандартный язык для бота. Стандарт: "ru".
    '''
    def __init__(self) -> None:
        self.DEBUG = bool(environ.get(f'TGBOT_DEBUG', False))
        self.DEV = bool(environ.get('TGBOT_DEV', False))
        self.TOKEN = str(environ.get(f'TGBOT_TOKEN', 'UNKNOWN'))
        self.TEST_TOKEN = str(environ.get(f'TGBOT_TEST_TOKEN', 'UNKNOWN'))
        self.VERSION = VERSION
        self.NAME = BOT_NAME
        self.ADMIN_ID = int(environ.get(f'TGBOT_ADMIN_ID', 0))
        self.DEFAULT_LANG = str(environ.get(f'TGBOT_DEFAULT_LANG', 'ru'))

    def getToken(self) -> str:
        '''Возвращает Telegram Bot Token основываясь на состоянии self.debug.

        Returns:
            str: Telegram Bot Token.
        '''
        return self.TEST_TOKEN if self.DEBUG else self.TOKEN


config = Configuration()
logging.basicConfig(
    format='[%(levelname)s] %(name)s (%(lineno)d) >> %(message)s',
    level=logging.DEBUG if config.DEBUG else logging.INFO)
logging.getLogger('asyncio').setLevel(logging.DEBUG if config.DEV else logging.INFO)
logging.getLogger('aiogram').setLevel(logging.DEBUG if config.DEV else logging.INFO)
