# -*- coding: utf-8 -*-
#
#  F_60893 - Database.
#  Created by LulzLoL231 at 11/6/21
#
from datetime import datetime
import logging
from typing import Any, Coroutine, Dict, Optional, Union

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
            access          bool DEFAULT false,
            premium         bool DEFAULT false,
            premium_start   timestamp,
            premium_end     timestamp,
            language        text DEFAULT \'ru\',
            id_binance      text,
            secret_binance  text,
            id_gate         text,
            secret_gate     text,
            order_amount    integer DEFAULT 100,
            take_profit     integer DEFAULT 10,
            stop_market     integer DEFAULT 3
        );'''
        await conn.execute(sql)

    @DBConnect
    async def set_access(self, uid: int, access: bool, conn: Connection) -> bool:
        '''Установка access.

        Args:
            uid (int): Telegram userID.
            access (bool): Access to lk.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'UPDATE bot_users SET access=$1 WHERE uid=$2'
        res = await conn.execute(sql, access, uid)
        return bool(res)

    @DBConnect
    async def set_order_amount(self, uid: int, amount: int, conn: Connection) -> bool:
        '''Установка суммы ордера.

        Args:
            uid (int): Telegram userID.
            amount (int): Orger amount.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'UPDATE bot_users SET amount=$1 WHERE uid=$2'
        res = await conn.execute(sql, amount, uid)
        return bool(res)

    @DBConnect
    async def set_take_profit(self, uid: int, take_profit: int, conn: Connection) -> bool:
        '''Установка take profit.

        Args:
            uid (int): Telegram userID.
            take_profit (int): Take profit %.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'UPDATE bot_users SET take_profit=$1 WHERE uid=$2'
        res = await conn.execute(sql, take_profit, uid)
        return bool(res)

    @DBConnect
    async def set_stop_market(self, uid: int, stop_market: int, conn: Connection) -> bool:
        '''Установка stop_market.

        Args:
            uid (int): Telegram userID.
            stop_market (int): Stop market %.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'UPDATE bot_users SET stop_market=$1 WHERE uid=$2'
        res = await conn.execute(sql, stop_market, uid)
        return bool(res)

    @DBConnect
    async def set_binance(self, uid: int, id: str, secret: str, conn: Connection) -> bool:
        '''Установка ключей для Binance.

        Args:
            uid (int): Telegram userID.
            id (str): Binance API ID.
            secret (str): Binance API secret.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'UPDATE bot_users SET id_binance=$1, secret_binance=$2 WHERE uid=$3;'
        res = await conn.execute(sql, id, secret, uid)

    @DBConnect
    async def set_gate(self, uid: int, id: str, secret: str, conn: Connection) -> bool:
        '''Установка ключей для Gate.

        Args:
            uid (int): Telegram userID.
            id (str): Gate API ID.
            secret (str): Gate API secret.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'UPDATE bot_users SET id_gate=$1, secret_gate=$2 WHERE uid=$3;'
        res = await conn.execute(sql, id, secret, uid)

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
    async def get_user(self, uid: int, conn: Connection) -> Optional[Union[dict, None]]:
        '''Возвращает пользователя по Telegram userID.

        Args:
            uid (int): Talagram userID.
            conn (Connection): DB Connection.

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
        res = await conn.execute(sql, uid, 'ru')
        if res:
            return True
        return False

    @DBConnect
    async def del_user(self, uid: int, conn: Connection) -> bool:
        '''Удаление пользователя.

        Args:
            uid (int): Telegram userID.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'DELETE FROM bot_users WHERE uid=$1'
        res = await conn.execute(sql, uid)
        if res:
            return True
        return False

    @DBConnect
    async def set_user_lang(self, uid: int, lang: str, conn: Connection) -> bool:
        '''Изменяет язык бота для пользователя.

        Args:
            uid (int): Telegram userID.
            lang (str): language name.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'UPDATE bot_users SET language = $1 WHERE uid = $2'
        res = await conn.execute(sql, lang, uid)
        return bool(res)

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

    @DBConnect
    async def start_premium(self, uid: int, end: datetime, conn: Connection) -> bool:
        '''Активирует премиум для пользователя.

        Args:
            uid (int): Telegram userID.
            end (datetime): premium end datetime.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        sql = 'UPDATE bot_users SET premium=true, premium_start=$1, premium_end=$2 WHERE uid=$3'
        res = await conn.execute(sql, datetime.now(), end, uid)
        return bool(res)

    @DBConnect
    async def end_premium(self, uid: int, conn: Connection) -> bool:
        '''Деактивирует премиум для пользователя.

        Args:
            uid (int): Telegram userID.
            conn (Connection): DB connection.

        Returns:
            bool: Boolean.
        '''
        res = await conn.execute('UPDATE bot_users SET premium=false, premium_start=null, premium_end=null WHERE uid=$1', uid)
        return bool(res)

    @DBConnect
    async def get_premium(self, uid: int, conn: Connection) -> Optional[Union[None, Dict[str, Any]]]:
        '''Возврашает статус премиума для пользователя.

        Args:
            uid (int): Telegram userID.
            conn (Connection): DB connection.

        Returns:
            Optional[Union[None, Dict[str, Any]]]: premium status or None.
        '''
        res = await conn.fetchrow('SELECT premium, premium_start, premium_end FROM bot_users WHERE uid=$1', uid)
        if res:
            return dict(res)
        return None
