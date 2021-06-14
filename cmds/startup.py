# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: startup.
#  Created by LulzLoL231 at 10/6/21
#
from typing import Any, Dict
from logging import getLogger
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from emojis import Emojis
from config import config
from runtime import bot, langs, db
from .premium import check_payment


log = getLogger(config.NAME)


class txidStates(StatesGroup):
    txid = State()


@bot.callback_query_handler(lambda q: q.data == 'fs_buy_sub')
async def fs_buy_sub(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.fs_buy_sub": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(msg.chat.id)
    lang = langs.get_language(usr['language'])
    await txidStates.txid.set()
    await query.answer()
    await msg.edit_text(f'{lang.t("enter_txid")}')


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
    log.info(f'"cmds.startup.start": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    lang = langs.get_language()
    # TODO: Make "First startup" sequence.
    cnt = f'<code>{lang.t("check_auth")}...</code>'
    if query:
        ev = await msg.edit_text(cnt)
    else:
        ev = await msg.answer(cnt)
    log.debug('"cmds.startup.start": Checking DB...')
    usr = await db.get_user(uid=msg.chat.id)
    if usr is None:
        log.debug(f'"cmds.startup.start": User #{str(msg.chat.id)} not found in DB!')
        if config.DEV:
            log.debug(f'"cmds.startup.start": Registration disabled due development.')
            await ev.edit_text(f'{Emojis.error} <b>{lang.t("user_404")}</b>!')
            return None
        log.debug(f'"cmds.startup.start": Registration...')
        await ev.edit_text(f'<code>{lang.t("reg")}...</code>')
        stat = await db.add_user(uid=msg.chat.id)
        if stat:
            log.debug(f'"cmds.startup.start": User #{str(msg.chat.id)} added to DB.')
            usr = await db.get_user(uid=msg.chat.id)
            await first_startup(ev, usr)
            return None
        else:
            log.error(f'"cmds.startup.start" User #{str(msg.chat.id)} registration failed!')
            await ev.edit_text(f'{Emojis.error} <code>{lang.t("reg_err")}!</code>')
    else:
        log.debug(f'"cmds.startup.start": User #{str(msg.chat.id)} found in DB.')
        lang = langs.get_language(usr['language'])
        if usr['access'] is False:
            log.warning(f'"cmds.startup.start": User #{str(msg.chat.id)} trying get access to profile without subscription!')
            await first_startup(ev, usr)
            return None
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


async def first_startup(msg: types.Message, usr: Dict[str, Any]):
    log.info(f'"cmds.startup.first_startup": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    lang = langs.get_language(usr['language'])
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.usd} {lang.t("pay_sub")}',
        callback_data='fs_buy_sub'
    ))
    if usr['language'] == 'ru':
        lang_eng = langs.get_language('en')
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.english} {lang_eng.t("chg_lang")} {lang_eng.t("to")} {lang_eng.t("english")}',
            callback_data='fs_chg_lang_eng'
        ))
    else:
        lang_ru = langs.get_language('ru')
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.russia} {lang_ru.t("chg_lang")} {lang_ru.t("on")} {lang_ru.t("russian")}',
            callback_data='fs_chg_lang_ru'
        ))
    username = ''
    if msg.chat.first_name:
        username += msg.chat.first_name
        if msg.chat.last_name:
            username += f' {msg.chat.last_name}'
    await msg.edit_text(lang.t('fs_hi').format(username), reply_markup=key)


@bot.callback_query_handler(lambda q: q.data == 'fs_chg_lang_eng')
async def fs_chg_lang_eng(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.fs_chg_lang_eng": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await db.set_user_lang(uid=msg.chat.id, lang='en')
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language('en')
    await query.answer()
    await msg.edit_text(f'<code>{lang.t("lang")} {lang.t("changed").lower()}!</code>')
    await first_startup(msg, usr)


@bot.callback_query_handler(lambda q: q.data == 'fs_chg_lang_ru')
async def fs_chg_lang_ru(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.fs_chg_lang_ru": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await db.set_user_lang(uid=msg.chat.id, lang='ru')
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language('ru')
    await query.answer()
    await msg.edit_text(f'<code>{lang.t("language")} {lang.t("changed").lower()}!</code>')
    await first_startup(msg, usr)


@bot.message_handler(state=txidStates.txid)
async def fs_buy_sub_txid(msg: types.Message, state: FSMContext):
    log.info(
        f'"cmds.startup.fs_buy_sub_txid": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await msg.answer_chat_action(types.ChatActions.TYPING)
    await state.finish()
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    ev = await msg.answer(f'<code>{lang.t("checking_payment")}...</code>')
    await msg.answer_chat_action(types.ChatActions.TYPING)
    check = await check_payment(msg.text)
    key = types.InlineKeyboardMarkup()
    if check:
        ending = datetime.now() + timedelta(days=config.PREMIUM_DEFAULT_DAYS)
        await db.start_premium(uid=msg.chat.id, end=ending)
        await db.set_access(uid=msg.chat.id, access=True)
        cnt = f'{Emojis.ok} <b>{lang.t("thx_for_payment")}!</b>\n'
        cnt += f'{lang.t("to")}: {ending.ctime()}.'
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.back} {lang.t("go_to_main")}',
            callback_data='main_menu'
        ))
        await ev.edit_text(cnt)
    else:
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.back} {lang.t("try_again")}', callback_data='fs_buy_sub'))
        await ev.edit_text(f'{Emojis.warning} {lang.t("payment_err")}!')
    await ev.edit_reply_markup(key)
