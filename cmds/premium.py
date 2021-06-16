# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: premium.
#  Created by LulzLoL231 at 12/6/21
#
from logging import getLogger
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from runtime import bot, db, langs
from emojis import Emojis
from config import config


log = getLogger(config.NAME)


class txidStates(StatesGroup):
    getState = State()


async def check_payment(exp: int, txid: str) -> bool:
    '''Проверяет оплату премиума по txid.

    Args:
        txid (str): payment txid.

    Returns:
        bool: Boolean.
    '''
    log.debug(f'"cmds.premium.check_payment": exp: {str(exp)}; txid: {txid}.')
    # TODO: Make real txid processing.
    if txid == '0':  # FIXME: for development
        return True
    return False


@bot.callback_query_handler(lambda q: q.data == 'buy_premium')
async def query_settings(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.premium.query_settings": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    if usr:
        lang = langs.get_language(usr['language'])
        key = types.InlineKeyboardMarkup()
        premium = await db.get_premium(uid=usr['uid'])
        if premium['premium']:
            cnt = f'{Emojis.on} {lang.t("premium_active")}\n'
            cnt += f'{lang.t("from")}: {premium["premium_start"].ctime()}'
            cnt += f'{lang.t("to")}: {premium["premium_end"].ctime()}'
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
                callback_data='settings'
            ))
            await query.answer()
            await msg.edit_text(cnt)
        else:
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.usd}',
                callback_data='fs_buy_sub'
            ))
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
                callback_data='settings'
            ))
            await query.answer()
            await msg.edit_text(lang.t("pay_sub"))
            await msg.edit_reply_markup(key)
    else:
        await query.answer()
        await msg.edit_text(f'<code>{langs.get_language(config.DEFAULT_LANG).t("user_404")}</code>')
