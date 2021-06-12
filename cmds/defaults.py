# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: defaults.
#  Created by LulzLoL231 at 10/6/21
#
from logging import getLogger

from aiogram import types

from emojis import Emojis
from config import config
from runtime import bot, langs, db


log = getLogger(config.NAME)


@bot.callback_query_handler(lambda q: q.data == 'main_menu')
async def query_start(query: types.CallbackQuery):
    await query.answer()
    await start(query.message, True)


@bot.message_handler(commands='start')
async def start(msg: types.Message, query: bool = False):
    '''cmd "start": Запуск и авторизация пользователя.

    Args:
        msg (types.Message): Telegram message.
        query (bool): Message from query?
    '''
    log.info(f'"cmds.defaults.start": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    lang = langs.get_language()
    # TODO: Make "First startup" sequence.
    cnt = f'<code>{lang.t("check_auth")}...</code>'
    if query:
        ev = await msg.edit_text(cnt)
    else:
        ev = await msg.answer(cnt)
    log.debug('"cmds.defaults.start": Checking DB...')
    usr = await db.get_user(uid=msg.chat.id)
    if usr is None:
        log.debug(f'"cmds.defaults.start": User #{str(msg.chat.id)} not found in DB!')
        if config.DEV:
            log.debug(f'"cmds.defaults.start": Registration disabled due development.')
            await ev.edit_text(f'{Emojis.error} <b>{lang.t("user_404")}</b>!')
            return None
        log.debug(f'"cmds.defaults.start": Registration...')
        await ev.edit_text(f'<code>{lang.t("reg")}...</code>')
        stat = await db.add_user(uid=msg.chat.id)
        if stat:
            log.debug(f'"cmds.defaults.start": User #{str(msg.chat.id)} added to DB.')
            msg_cnt = f'<code>{lang.t("reg_ok")}!</code>\n'
        else:
            log.error(f'"cmds.defaults.start" User #{str(msg.chat.id)} registration failed!')
            await ev.edit_text(f'{Emojis.error} <code>{lang.t("reg_err")}!</code>')
    else:
        log.debug(f'"cmds.deafults.start": User #{str(msg.chat.id)} found in DB.')
        lang = langs.get_language(usr['language'])
        usr = await db.get_user(uid=msg.chat.id)
        if msg.chat.id == config.ADMIN_ID:
            msg_cnt = f'<code>{lang.t("admin_recog")}!</code>\n'
        else:
            msg_cnt = f'<code>{lang.t("user_recog")}!</code>\n'
    msg_cnt += f'{lang.t("hi")}, {msg.chat.first_name}! {Emojis.hi}'
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.pen} {lang.t("order")}',
        callback_data='order'
    ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.settings} {lang.t("settings")}',
        callback_data='settings'
    ))
    await ev.edit_text(msg_cnt, reply_markup=key)
