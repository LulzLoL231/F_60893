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


async def check_payment(txid: str) -> bool:
    '''Проверяет оплату премиума по txid.

    Args:
        txid (str): payment txid.

    Returns:
        bool: Boolean.
    '''
    log.debug(f'"cmds.premium.check_payment": txid: {txid}')
    # TODO: Make real txid processing.
    if txid == '0':  # FIXME: for development
        return True
    return False


@bot.callback_query_handler(lambda q: q.data == 'buy_premium')
async def query_settings(query: types.CallbackQuery):
    await query.answer()
    msg = query.message
    log.info(
        f'"cmds.premium.query_settings": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    if usr:
        lang = langs.get_language(usr['language'])
        key = types.InlineKeyboardMarkup()
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
            callback_data='settings'
        ))
        await msg.edit_text(f'<code>{lang.t("check_premium")}...</code>')
        premium = await db.get_premium(uid=usr['uid'])
        if premium['premium']:
            cnt = f'{Emojis.on} {lang.t("premium_active")}\n'
            cnt += f'{lang.t("from")}: {premium["premium_start"].ctime()}'
            cnt += f'{lang.t("to")}: {premium["premium_end"].ctime()}'
            await msg.edit_text(cnt)
        else:
            await txidStates.getState.set()
            await msg.edit_text(f'<b>{lang.t("enter_txid")}</b>')


@bot.message_handler(state=txidStates.getState)
async def check_txid(msg: types.Message, state: FSMContext):
    await state.finish()
    usr = await db.get_user(uid=msg.chat.id)
    log.info(
        f'"cmds.premium.check_txid": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    lang = langs.get_language(usr['language'])
    ev = await msg.answer(f'TXID: <b>{msg.text}</b>\n<code>{lang.t("checking_payment")}...</code>')
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
        callback_data='settings'
    ))
    status = await check_payment(msg.text)
    if status:
        ending = datetime.now() + timedelta(days=config.PREMIUM_DEFAULT_DAYS)
        await db.start_premium(uid=msg.chat.id, end=ending)
        cnt = f'{Emojis.ok} {lang.t("thx_for_payment")}!\n'
        cnt += f'{lang.t("to")}: {ending.ctime()}.'
        await ev.edit_text(cnt)
    else:
        await ev.edit_text(f'{Emojis.warning} {lang.t("payment_err")}!')
    await ev.edit_reply_markup(key)
