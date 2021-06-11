# -*- coding: utf-8 -*-
#
#  F_60893 - Database.
#  Created by LulzLoL231 at 11/6/21
#
import logging
from typing import Coroutine, Optional, Union

import asyncpg
from asyncpg.connection import Connection

from config import config


DSN = f'postgresql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{str(config.DB_PORT)}/'
DSN += f'{config.DB_BASE_NAME}?sslmode={config.DB_SSL}'


def DBConnect(func):
    async def wrap(self, *args, **kwargs):
        conn = await asyncpg.connect(DSN)
        res = await func(self, *args, **kwargs, conn=conn)
        await conn.close()
        return res
    return wrap


class Database:
    '''F_60893 DataBase class.
    '''
    def __init__(self) -> None:
        self.log = logging.getLogger('F_60893')
        self.log.debug(f'"database.Database.__init__": DSN: "{DSN}"')

    @DBConnect
    async def _check_table_exists(self, table: str, conn: Connection) -> bool:
        '''Private func: Check table exists.

        Args:
            conn (Connection): DB Connection.
            table (str): Table to search.

        Returns:
            bool: True if table exists, otherwise False.
        '''
        res = await conn.fetchrow("SELECT to_regclass($1);", table)
        return bool(res['to_regclass'])


    @DBConnect
    async def _create_bot_users_table(self, conn: Connection) -> None:
        '''Private func: Creates bot_users table.

        Args:
            conn (Connection): DB connection.
        '''
        sql = '''CREATE TABLE IF NOT EXISTS bot_users (
            uid             integer NOT NULL PRIMARY KEY,
            apis            tid,
            admin           bool DEFAULT false,
            premium         bool DEFAULT false,
            premium_start   timestamp,
            premium_end     timestamp
        );
        '''
        res = await conn.execute(sql)


    async def check_database(self) -> bool:
        '''Ищет необходимые для бота таблицы в выбранной БД, если каких-то нет - создаёт.

        Returns:
            bool: Если ошибок нет - True. Иначе False.
        '''
        self.log.info('"database.Database.check_database": Checking DB...')
        stat = await self.check_connection()
        if stat:
            users = await self._check_table_exists('bot_users')
            if users:
                self.log.info('"database.Database.check_database": Check complete!')
                return True
            else:
                self.log.warning('"database.Database.check_database": Table "bot_users" is not found! Creating...')
                stat = await self._create_bot_users_table()
                if stat:
                    self.log.info('"database.Database.cehck_database": Table "bot_users" successfull created!')
        else:
            self.log.error('"database.Database.check_database": Error while checking connection!')
            return False

    @DBConnect
    async def get_user(self, conn: Connection, uid: int) -> Optional[Union[dict, None]]:
        '''Возвращает пользователя по Telegram userID.

        Args:
            conn (Connection): DB Connection.
            uid (int): Talagram userID.

        Returns:
            Optional[Union[dict, None]]: User dict or None.
        '''
        res = await conn.fetchrow('SELECT * FROM bot_users WHERE uid = $1', uid)
        if res:
            return dict(res)
        return None

    @DBConnect
    async def add_user(self, uid: int, conn: Connection) -> bool:
        '''Регистрация нового пользователя.

        Args:
            uid (int): Telegram userID.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'INSERT INTO bot_users (uid, language) VALUES ($1, $2)'
        stat = await conn.execute(sql, uid, 'ru')
        if stat:
            return True
        return False

    @DBConnect
    async def check_connection(self, conn: Connection) -> bool:
        '''Проверяет подключение к БД.

        Args:
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        res = await conn.fetchrow('SELECT version();')
        if res:
            self.log.info('"database.Database.check_connection": Connection Established!')
            self.log.debug(f'"database.Database.check_connection": {res["version"]}')
            return True
        else:
            self.log.error('"database.Database.check_connection": Unknown error when trying connect to DB!')
            return False
