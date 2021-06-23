# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: startup.
#  Created by LulzLoL231 at 10/6/21
#
from typing import Any, Dict
from logging import getLogger
from datetime import datetime, timedelta

from aiogram import types

from emojis import Emojis
from config import config
from runtime import bot, langs, db, bot_user
from database import DBConnect


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
    log.info(f'"cmds.startup.start": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    if query:
        await msg.answer_chat_action(types.ChatActions.TYPING)
    else:
        await msg.answer_chat_action(types.ChatActions.TYPING)
    log.debug('"cmds.startup.start": Checking DB...')
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(config.DEFAULT_LANG)
    if usr is None:
        log.debug(f'"cmds.startup.start": User #{str(msg.chat.id)} not found in DB!')
        log.debug(f'"cmds.startup.start": Registration...')
        stat = await db.add_user(uid=msg.chat.id)
        if stat:
            log.debug(f'"cmds.startup.start": User #{str(msg.chat.id)} added to DB.')
            usr = await db.get_user(uid=msg.chat.id)
            await first_startup(msg, usr)
            return None
        else:
            log.error(f'"cmds.startup.start" User #{str(msg.chat.id)} registration failed!')
            if query:
                await msg.edit_text(f'{Emojis.error} <code>{lang.t("reg_err")}!</code>')
            else:
                await msg.answer(f'{Emojis.error} <code>{lang.t("reg_err")}!</code>')
    else:
        lang = langs.get_language(usr['language'])
        log.debug(f'"cmds.startup.start": User #{str(msg.chat.id)} found in DB.')
        if usr['access'] is False:
            log.warning(f'"cmds.startup.start": User #{str(msg.chat.id)} trying get access to profile without subscription!')
            if query:
                await first_startup(msg, usr)
            else:
                await first_startup(msg, usr)
            return None
        if msg.chat.id == config.ADMIN_ID:
            msg_cnt = f'<code>{lang.t("admin_recog")}!</code>\n'
        else:
            msg_cnt = f'<code>{lang.t("user_recog")}!</code>\n'
    msg_cnt += f'{lang.t("hi")}, {msg.chat.first_name}! {Emojis.hi}'
    key = types.InlineKeyboardMarkup()
    if usr['premium'] is False:
        if usr['premium_start']:
            msg_cnt += f'\n\n<b>{lang.t("sub_off")}!</b>'
        key.add(
            types.InlineKeyboardButton(
                text=f'{Emojis.usd} {lang.t("pay_sub")}',
                callback_data='fs_buy_sub'
            )
        )
    if usr['premium'] and (usr['premium_end'] - datetime.now()).total_seconds() <= config.PREMIUM_EXP_NOTIFY_SECS:
        msg_cnt += f'\n\n<b>{lang.t("dont_forget_renew")}!</b>'
        key.add(
            types.InlineKeyboardButton(
                text=f'{Emojis.renew} {lang.t("renew_sub")}',
                callback_data='renew_premium'
            )
        )
    binance = (usr["id_binance"] and usr["secret_binance"])
    if binance:
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.pen} {lang.t("order")}',
            callback_data='order'
        ))
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.info} {lang.t("about")}',
            callback_data='about'
        ))
    else:
        msg_cnt += f'\n\n<b>{lang.t("plz_install_apis")}!</b>'
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.settings} {lang.t("apis")}',
            callback_data='apis'
        ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.settings} {lang.t("settings")}',
        callback_data='settings'
    ))
    if query:
        await msg.edit_text(msg_cnt)
        await msg.edit_reply_markup(key)
    else:
        await msg.answer(msg_cnt, reply_markup=key)


async def first_startup(msg: types.Message, usr: Dict[str, Any]):
    log.info(f'"cmds.startup.first_startup": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    lang = langs.get_language(usr['language'])
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.magic} {lang.t("begin_start")}',
        callback_data='begin'
    ))
    if usr['language'] == 'ru':
        lang_eng = langs.get_language('en')
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.english} {lang_eng.t("chg_lang")} {lang_eng.t("to")} {lang_eng.t("english")}',
            callback_data='fs_chg_lang_eng'
        ))
        lang_es = langs.get_language('es')
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.espanol} {lang_es.t("chg_lang")} {lang_es.t("to")} {lang_es.t("espanol")}',
            callback_data='fs_chg_lang_es'
        ))
    elif usr['language'] == 'en':
        lang_ru = langs.get_language('ru')
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.russia} {lang_ru.t("chg_lang")} {lang_ru.t("on")} {lang_ru.t("russian")}',
            callback_data='fs_chg_lang_ru'
        ))
        lang_es = langs.get_language('es')
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.espanol} {lang_es.t("chg_lang")} {lang_es.t("to")} {lang_es.t("espanol")}',
            callback_data='fs_chg_lang_es'
        ))
    elif usr['language'] == 'es':
        lang_eng = langs.get_language('en')
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.english} {lang_eng.t("chg_lang")} {lang_eng.t("to")} {lang_eng.t("english")}',
            callback_data='fs_chg_lang_eng'
        ))
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
    if msg.from_user != bot_user:
        await msg.answer(
            lang.t('start').format(
                first_name=username,
                coolface=Emojis.coolface,
                magic=Emojis.magic),
            reply_markup=key
        )
    else:
        await msg.edit_text(
            lang.t('start').format(
                first_name=username,
                coolface=Emojis.coolface,
                magic=Emojis.magic),
            reply_markup=key
        )


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


@bot.callback_query_handler(lambda q: q.data == 'fs_chg_lang_es')
async def fs_chg_lang_es(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.fs_chg_lang_es": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await db.set_user_lang(uid=msg.chat.id, lang='es')
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language('es')
    await query.answer()
    await msg.edit_text(f'<code>{lang.t("language")} {lang.t("changed").lower()}!</code>')
    await first_startup(msg, usr)





@bot.message_handler(commands=['_set_sub_expiration'])
async def _set_sub_expiration(msg: types.Message):
    # TODO: Need to delete from Production!
    '''Симулирует что до истечения подписки остаётся меньше 1 дня.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(
        f'"cmds.startup._set_sub_expiration": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await msg.answer_chat_action(types.ChatActions.TYPING)

    @DBConnect
    async def set_premium(_, uid, premium_end, conn):
        await conn.execute(f'UPDATE {config.DB_USERS_TABLE_NAME} SET premium_end=$1 WHERE uid=$2', premium_end, uid)
    
    await set_premium(None, uid=msg.chat.id, premium_end=datetime.now() + timedelta(hours=1))
    await msg.answer('<code>ok</code>')


@bot.message_handler(commands=['_set_sub_expired'])
async def _set_sub_expired(msg: types.Message):
    # TODO: Need to delete from Production!
    '''Симулирует что подписка истекла.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(
        f'"cmds.startup._set_sub_expired": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await msg.answer_chat_action(types.ChatActions.TYPING)
    await db.end_premium(uid=msg.chat.id)
    await msg.answer('<code>ok</code>')
