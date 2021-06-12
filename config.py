# -*- coding: utf-8 -*-
#
#  F_60893 - configuration.
#  Created by LulzLoL231 at 10/6/21
#
import logging
from os import environ


BOT_NAME = 'F_60893'
VERSION = '0.8.8-beta'


class Configuration:
    '''Конфигурация бота.

    Args:
        DEBUG (bool) - Дебаг режим. Стандарт: False.
        DEV (bool) - Режим разработчика. Стандарт: False.
        TOKEN (str) - Основной токен бота. Стандарт: "UNKNOWN".
        TEST_TOKEN (str) - Тестовый токен бота. Стандарт: "UNKNOWN".
        ADMIN_ID (int) - Telegram userID администратора. Стандарт: 0.
        DEFAULT_LANG (str) - Стандартный язык для бота. Стандарт: "ru".
        DB_HOST (str) - Хост БД. Стандарт: "localhost".
        DB_PORT (int) - Порт БД. Стандарт: 5432.
        DB_USERNAME (str) - Пользователь БД. Стандарт: "UNKNOWN".
        DB_PASSWORD (str) - Пароль пользователя БД. Стандарт: "UNKNOWN".
        DB_BASE_NAME (str) - Имя базы в БД. Стандарт: self.DB_USERNAME.
        DB_SSL (str) - Режим SSL. Стандарт: "prefer".
        DB_SSL_ROOTCERT (PathLike) - Путь к корневому сертификату БД. Стандарт: "". 
    '''
    def __init__(self) -> None:
        self.DEV = True if bool(VERSION.endswith(
            '-dev')) else bool(environ.get('TGBOT_DEV', False))
        if self.DEV:
            print('DEVELOPMENT MODE!')
        self.DEBUG = bool(environ.get('TGBOT_DEBUG', False))
        self.TOKEN = str(environ.get('TGBOT_TOKEN', 'UNKNOWN'))
        self.TEST_TOKEN = str(environ.get('TGBOT_TEST_TOKEN', 'UNKNOWN'))
        self.VERSION = VERSION
        self.NAME = BOT_NAME
        self.ADMIN_ID = int(environ.get('TGBOT_ADMIN_ID', 0))
        self.DEFAULT_LANG = str(environ.get('TGBOT_DEFAULT_LANG', 'ru'))
        self.DB_HOST = environ.get('TGBOT_DB_HOST', 'localhost')
        self.DB_PORT = environ.get('TGBOT_DB_PORT', 5432)
        self.DB_USERNAME = environ.get('TGBOT_DB_USERNAME', 'UNKNOWN')
        self.DB_PASSWORD = environ.get('TGBOT_DB_PASSWORD', 'UNKNOWN')
        self.DB_BASE_NAME = environ.get('TGBOT_DB_BASE_NAME', self.DB_USERNAME)
        self.DB_SSL = environ.get('TGBOT_DB_SSL', 'prefer')
        self.DB_SSL_ROOTCERT = environ.get('TGBOT_DB_SSL_ROOTCERT', '')
        self.PREMIUM_DEFAULT_DAYS = 30

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
logging.getLogger('asyncio').setLevel(logging.INFO)
logging.getLogger('aiogram').setLevel(logging.INFO)
