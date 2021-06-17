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
from database import DBConnect
from .premium import check_payment


log = getLogger(config.NAME)


class txidStates(StatesGroup):
    txid = State()


@bot.callback_query_handler(lambda q: q.data == 'fs_buy_sub')
@bot.callback_query_handler(lambda q: q.data == 'renew_premium')
async def fs_buy_sub(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.fs_buy_sub": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(msg.chat.id)
    lang = langs.get_language(usr['language'])
    key = types.InlineKeyboardMarkup()
    key.row(
        types.InlineKeyboardButton(
            text=f'1 {lang.t("mon1")}',
            callback_data='sub_200'
        ),
        types.InlineKeyboardButton(
            text=f'3 {lang.t("mon2")}',
            callback_data='sub_540'
        )
    )
    key.row(
        types.InlineKeyboardButton(
            text=f'6 {lang.t("mon3")}',
            callback_data='sub_1000'
        ),
        types.InlineKeyboardButton(
            text=f'12 {lang.t("mon3")}',
            callback_data='sub_1900'
        )
    )
    key.row(types.InlineKeyboardButton(
        text=f'{lang.t("forever")}',
        callback_data='sub_4000'
    ))
    await query.answer()
    await msg.edit_text(f'{lang.t("how_much_mon")}?')
    await msg.edit_reply_markup(key)


@bot.callback_query_handler(lambda q: q.data == 'sub_200')
async def sub_200(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.sub_200": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(msg.chat.id)
    lang = langs.get_language(usr['language'])
    state = bot.current_state(chat=msg.chat.id)
    await txidStates.txid.set()
    await state.update_data({'exp': config.PREMIUMS[200], 'usdt': 200})
    await msg.edit_text(f'<b>{lang.t("you_must_paid").format("200")}</b>\n{lang.t("enter_txid")}')


@bot.callback_query_handler(lambda q: q.data == 'sub_540')
async def sub_540(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.sub_540": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(msg.chat.id)
    lang = langs.get_language(usr['language'])
    state = bot.current_state(chat=msg.chat.id)
    await txidStates.txid.set()
    await state.update_data({'exp': config.PREMIUMS[540], 'usdt': 540})
    await msg.edit_text(f'<b>{lang.t("you_must_paid").format("540")}</b>\n{lang.t("enter_txid")}')


@bot.callback_query_handler(lambda q: q.data == 'sub_1000')
async def sub_1000(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.sub_1000": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(msg.chat.id)
    lang = langs.get_language(usr['language'])
    state = bot.current_state(chat=msg.chat.id)
    await txidStates.txid.set()
    await state.update_data({'exp': config.PREMIUMS[1000], 'usdt': 1000})
    await msg.edit_text(f'<b>{lang.t("you_must_paid").format("1000")}</b>\n{lang.t("enter_txid")}')


@bot.callback_query_handler(lambda q: q.data == 'sub_1900')
async def sub_1900(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.sub_1900": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(msg.chat.id)
    lang = langs.get_language(usr['language'])
    state = bot.current_state(chat=msg.chat.id)
    await txidStates.txid.set()
    await state.update_data({'exp': config.PREMIUMS[1900], 'usdt': 1900})
    await msg.edit_text(f'<b>{lang.t("you_must_paid").format("1900")}</b>\n{lang.t("enter_txid")}')


@bot.callback_query_handler(lambda q: q.data == 'sub_4000')
async def sub_4000(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.startup.sub_4000": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(msg.chat.id)
    lang = langs.get_language(usr['language'])
    state = bot.current_state(chat=msg.chat.id)
    await txidStates.txid.set()
    await state.update_data({'exp': config.PREMIUMS[4000], 'usdt': 4000})
    await msg.edit_text(f'<b>{lang.t("you_must_paid").format("4000")}</b>\n{lang.t("enter_txid")}')


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
    cnt = f'<code>{lang.t("check_auth")}...</code>'
    if query:
        ev = await msg.edit_text(cnt)
    else:
        ev = await msg.answer(cnt)
    log.debug('"cmds.startup.start": Checking DB...')
    usr = await db.get_user(uid=msg.chat.id)
    if usr is None:
        log.debug(f'"cmds.startup.start": User #{str(msg.chat.id)} not found in DB!')
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


@bot.message_handler(state=txidStates.txid)
async def fs_buy_sub_txid(msg: types.Message, state: FSMContext):
    log.info(
        f'"cmds.startup.fs_buy_sub_txid": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await msg.answer_chat_action(types.ChatActions.TYPING)
    data = await state.get_data()
    await state.finish()
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    cnt = f'<b>USDT</b>: <code>{data["usdt"]}</code>\n'
    cnt += f'<b>TXID</b>: <code>{msg.text}</code>\n'
    cnt += f'\n<code>{lang.t("checking_payment")}...</code>'
    ev = await msg.answer(cnt)
    await msg.answer_chat_action(types.ChatActions.TYPING)
    check = await check_payment(data['exp'], msg.text)
    key = types.InlineKeyboardMarkup()
    if check:
        ending = datetime.now() + timedelta(days=data['exp'])
        await db.start_premium(uid=msg.chat.id, end=ending)
        await db.set_access(uid=msg.chat.id, access=True)
        cnt = f'{Emojis.ok} <b>{lang.t("thx_for_payment")}!</b>\n'
        cnt += f'{lang.t("valid_until")}: {ending.ctime()}.'
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.key} {lang.t("go_to_main")}',
            callback_data='main_menu'
        ))
        await ev.edit_text(cnt)
    else:
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.back} {lang.t("try_again")}', callback_data='fs_buy_sub'))
        await ev.edit_text(f'{Emojis.warning} {lang.t("payment_err")}!')
    await ev.edit_reply_markup(key)


@bot.message_handler(commands=['_set_sub_expiration'])
async def _set_sub_expiration(msg: types.Message):
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
    '''Симулирует что подписка истекла.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(
        f'"cmds.startup._set_sub_expired": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await msg.answer_chat_action(types.ChatActions.TYPING)
    await db.end_premium(uid=msg.chat.id)
    await msg.answer('<code>ok</code>')
