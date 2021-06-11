# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: defaults.
#  Created by LulzLoL231 at 10/6/21
#
from logging import getLogger

from aiogram import types

from emojis import Emojis
from runtime import bot, langs, db
from config import config, USR_TEMP


log = getLogger(config.NAME)


@bot.message_handler(commands='start')
async def start(msg: types.Message):
    '''cmd "start": Запуск и авторизация пользователя.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(f'"cmds.defaults.start": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    lang = langs.get_language()
    ev = await msg.answer(f'<code>{lang.get("check_auth")}...</code>')
    log.debug('"cmds.defaults.start": Checking DB...')
    if msg.chat.id not in db['users']:
        await ev.edit_text(f'<code>{lang.get("reg")}...</code>')
        usr = USR_TEMP.copy()
        usr['uid'] = msg.chat.id
        usr['lang'] = config.DEFAULT_LANG
        db['users'].update({msg.chat.id: usr})
        log.debug(f'"cmds.defaults.start": User #{str(msg.chat.id)} added to DB.')
        msg_cnt = f'<code>{lang.get("reg_ok")}!</code>\n'
    else:
        log.debug(f'"cmds.deafults.start": User #{str(msg.chat.id)} found in DB.')
        msg_cnt = f'<code>{lang.get("user_recog")}!</code>\n'
    msg_cnt += f'{lang.get("hi")}, {msg.chat.first_name}! {Emojis.hi}'
    await ev.edit_text(msg_cnt)