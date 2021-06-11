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


class connect(object):
    '''DB connect resolver.
    '''
    def __init__(self, dsn: str):
        self.dsn = dsn

    def __call__(self, func: Coroutine):
        async def wrapped():
            conn = await asyncpg.connect(self.dsn)
            result = await func(conn)
            await conn.close()
            return result
        return wrapped


DSN = f'postgresql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{str(config.DB_PORT)}'
DSN += f'{config.DB_BASE_NAME}?sslmode={config.DB_SSL}&sslrootcert={config.DB_SSL_ROOTCERT}'


class Database:
    '''F_60893 DataBase class.
    '''
    def __init__(self) -> None:
        self.log = logging.getLogger('F_60893')

    @connect(DSN)
    async def _check_users_table(self, conn: Connection) -> bool:
        '''Private func: Check if "bot_users" table exists.

        Args:
            conn (Connection): DB Connection.

        Returns:
            bool: True if table exists, otherwise False.
        '''
        res = await conn.fetchrow('''SELECT EXISTS (
        SELECT FROM pg_tables
        WHERE  schemaname = "public"
        AND    tablename  = "bot_users");''')
        return res.exists


    async def check_database(self) -> bool:
        '''Ищет необходимые для бота таблицы в выбранной БД, если каких-то нет - создаёт.

        Returns:
            bool: Если ошибок нет - True. Иначе False.
        '''
        self.log.info('"database.Database.check_database": Checking DB...')
        users = await self._check_users_table()
        if users:
            self.log.info('"database.Database.check_database": Check complete!')
            return True
        else:
            self.log.error('"database.Database.check_database": Table "bot_users" is not found!')
            return False

    @connect(DSN)
    async def get_user(self, conn: Connection, uid: int) -> Optional[Union[dict, None]]:
        '''Возвращает пользователя по Telegram userID.

        Args:
            conn (Connection): DB Connection.
            uid (int): Talagram userID.

        Returns:
            Optional[Union[dict, None]]: User dict or None.
        '''
        res = await conn.fetchrow('SELECT * FROM "bot_users" WHERE uid = $1', uid)
        if res:
            return dict(res)
        return None
