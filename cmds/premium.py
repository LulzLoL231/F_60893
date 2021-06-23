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


async def check_payment(sum: int, txid: str) -> bool:
    '''Проверяет оплату премиума по txid.

    Args:
        sum (int): payment sum.
        txid (str): payment txid.

    Returns:
        bool: Boolean.
    '''
    log.debug(f'"cmds.premium.check_payment": sum: {str(sum)}; txid: {txid}.')
    # TODO: Make real txid processing.
    if txid == '0':  # FIXME: for development
        return True
    return False


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
    check = await check_payment(data['usdt'], msg.text)
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
            await fs_buy_sub(query)
    else:
        await query.answer()
        await msg.edit_text(f'<code>{langs.get_language(config.DEFAULT_LANG).t("user_404")}</code>')
