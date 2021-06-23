# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: order.
#  Created by LulzLoL231 at 13/6/21
#
from logging import getLogger

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from emojis import Emojis
from config import config
from runtime import bot, db, langs


log = getLogger(config.NAME)


class amountStatesUSDT(StatesGroup):
    amount = State()


class takeProfitStatesUSDT(StatesGroup):
    take_profit = State()


class stopMarketStatesUSDT(StatesGroup):
    stop_market = State()


class amountStatesDoge(StatesGroup):
    amount = State()


class takeProfitStatesDoge(StatesGroup):
    take_profit = State()


class stopMarketStatesDoge(StatesGroup):
    stop_market = State()


@bot.callback_query_handler(lambda q: q.data == 'order')
async def order(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    cnt = f'''{Emojis.usd} <b>{lang.t("order_status_active") if usr["premium"] else lang.t("order_status_disabled")}</b>

<b>{lang.t("detail")} USDT</b>
{lang.t("amount")}: <b>{usr["order_amount_usdt"]} USDT</b>
{lang.t("take_profit")}: <b>{usr["take_profit_usdt"] if bool(usr["take_profit_usdt"]) else lang.t("not_used")}{"%" if bool(usr["take_profit_usdt"]) else "."}</b>
{lang.t("stop_market")}: <b>{usr["stop_market_usdt"] if bool(usr["stop_market_usdt"]) else lang.t("not_used")}{"%" if bool(usr["stop_market_usdt"]) else "."}</b>

<b>{lang.t("detail")} DogeCoin</b>
{lang.t("amount")}: <b>{usr["order_amount_doge"]} Doge</b>
{lang.t("take_profit")}: <b>{usr["take_profit_doge"] if bool(usr["take_profit_doge"]) else lang.t("not_used")}{"%" if bool(usr["take_profit_doge"]) else "."}</b>
{lang.t("stop_market")}: <b>{usr["stop_market_doge"] if bool(usr["stop_market_doge"]) else lang.t("not_used")}{"%" if bool(usr["stop_market_doge"]) else "."}</b>
'''
    key = types.InlineKeyboardMarkup()
    if usr['premium']:
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.pen} "{lang.t("amount")}" USDT',
            callback_data='change_amount_usdt'
        ))
        key.row(types.InlineKeyboardButton(
            text=f'{Emojis.pen} "{lang.t("take_profit")}" USDT',
            callback_data='change_take_profit_usdt'
        ), types.InlineKeyboardButton(
            text=f'{Emojis.pen} "{lang.t("stop_market")}" USDT',
            callback_data='change_stop_market_usdt'
        ))
        key.row(types.InlineKeyboardButton(
            text=f'{Emojis.no} "{lang.t("take_profit")}" USDT',
            callback_data='disable_take_profit_usdt'
        ), types.InlineKeyboardButton(
            text=f'{Emojis.no} "{lang.t("stop_market")}" USDT',
            callback_data='disable_stop_market_usdt'
        ))
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.pen} "{lang.t("amount")}" Doge',
            callback_data='change_amount_doge'
        ))
        key.row(types.InlineKeyboardButton(
            text=f'{Emojis.pen} "{lang.t("take_profit")}" Doge',
            callback_data='change_take_profit_doge'
        ), types.InlineKeyboardButton(
            text=f'{Emojis.pen} "{lang.t("stop_market")}" Doge',
            callback_data='change_stop_market_doge'
        ))
        key.row(types.InlineKeyboardButton(
            text=f'{Emojis.no} "{lang.t("take_profit")}" Doge',
            callback_data='disable_take_profit_doge'
        ), types.InlineKeyboardButton(
            text=f'{Emojis.no} "{lang.t("stop_market")}" Doge',
            callback_data='disable_stop_market_doge'
        ))
    else:
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.usd} {lang.t("pay_sub")}',
            callback_data='fs_buy_sub'
        ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("main_menu").lower()}',
        callback_data='main_menu'
    ))
    await query.answer()
    await msg.edit_text(cnt)
    await msg.edit_reply_markup(key)


@bot.callback_query_handler(lambda q: q.data == 'change_amount_usdt')
async def enter_amount_usdt(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await amountStatesUSDT.amount.set()
    await query.answer()
    await msg.edit_text(lang.t("change_amount"))


@bot.message_handler(state=amountStatesUSDT.amount)
async def change_amount_usdt(msg: types.Message, state: FSMContext):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    if msg.text.isdigit() is False:
        await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_amount")}</b>\n{lang.t("amount")} {lang.t("must_be_digit").lower()}!')
    else:
        if int(msg.text) <= 250000 and int(msg.text) >= 10:
            await state.finish()
            await db.set_order_amount_usdt(uid=usr['uid'], amount=int(msg.text))
            key = types.InlineKeyboardMarkup()
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
                callback_data='order'
            ))
            await msg.answer(f'{Emojis.ok} {lang.t("setted_amount")}', reply_markup=key)
        else:
            await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_amount")}</b>\n{lang.t("from_10_to_250000")}!')


@bot.callback_query_handler(lambda q: q.data == 'change_take_profit_usdt')
async def enter_take_profit_usdt(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await takeProfitStatesUSDT.take_profit.set()
    await query.answer()
    await msg.edit_text(lang.t("change_take_profit"))


@bot.message_handler(state=takeProfitStatesUSDT.take_profit)
async def change_take_profit_usdt(msg: types.Message, state: FSMContext):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    if msg.text.isdigit() is False:
        await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_take_profit")}</b>\nTake profit {lang.t("must_be_digit").lower()}!')
    else:
        if int(msg.text) <= 100 and int(msg.text) >= 0:
            await state.finish()
            await db.set_take_profit_usdt(uid=usr['uid'], take_profit=int(msg.text))
            key = types.InlineKeyboardMarkup()
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
                callback_data='order'
            ))
            await msg.answer(f'{Emojis.ok} {lang.t("setted_take_profit")}', reply_markup=key)
        else:
            await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_take_profit")}</b>\n{lang.t("from_0_to_100").format("take profit")}!')


@bot.callback_query_handler(lambda q: q.data == 'disable_take_profit_usdt')
async def dont_use_take_profit_usdt(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await db.set_take_profit_usdt(uid=usr['uid'], take_profit=0)
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
        callback_data='order'
    ))
    await query.answer()
    await msg.edit_text(f'{Emojis.ok} {lang.t("setted_take_profit")}', reply_markup=key)


@bot.callback_query_handler(lambda q: q.data == 'change_stop_market_usdt')
async def enter_stop_market_usdt(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await stopMarketStatesUSDT.stop_market.set()
    await query.answer()
    await msg.edit_text(lang.t("change_stop_market"))


@bot.message_handler(state=stopMarketStatesUSDT.stop_market)
async def change_stop_market_usdt(msg: types.Message, state: FSMContext):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    if msg.text.isdigit() is False:
        await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_stop_market")}</b>\nStop market {lang.t("must_be_digit").lower()}!')
    else:
        if int(msg.text) <= 100 and int(msg.text) >= 0:
            await state.finish()
            await db.set_stop_market_usdt(uid=usr['uid'], stop_market=int(msg.text))
            key = types.InlineKeyboardMarkup()
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
                callback_data='order'
            ))
            await msg.answer(f'{Emojis.ok} {lang.t("setted_stop_market")}', reply_markup=key)
        else:
            await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_stop_market")}</b>\n{lang.t("from_0_to_100").format("stop market")}!')


@bot.callback_query_handler(lambda q: q.data == 'disable_stop_market_usdt')
async def dont_use_stop_market_usdt(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await db.set_stop_market_usdt(uid=usr['uid'], stop_market=0)
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
        callback_data='order'
    ))
    await query.answer()
    await msg.edit_text(f'{Emojis.ok} {lang.t("setted_stop_market")}', reply_markup=key)


@bot.callback_query_handler(lambda q: q.data == 'change_amount_doge')
async def enter_amount_doge(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await amountStatesDoge.amount.set()
    await query.answer()
    await msg.edit_text(lang.t("change_amount"))


@bot.message_handler(state=amountStatesDoge.amount)
async def change_amount_doge(msg: types.Message, state: FSMContext):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    if msg.text.isdigit() is False:
        await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_amount")}</b>\n{lang.t("amount")} {lang.t("must_be_digit").lower()}!')
    else:
        if int(msg.text) <= 250000 and int(msg.text) >= 10:
            await state.finish()
            await db.set_order_amount_doge(uid=usr['uid'], amount=int(msg.text))
            key = types.InlineKeyboardMarkup()
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
                callback_data='order'
            ))
            await msg.answer(f'{Emojis.ok} {lang.t("setted_amount")}', reply_markup=key)
        else:
            await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_amount")}</b>\n{lang.t("from_10_to_250000")}!')


@bot.callback_query_handler(lambda q: q.data == 'change_take_profit_doge')
async def enter_take_profit_doge(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await takeProfitStatesDoge.take_profit.set()
    await query.answer()
    await msg.edit_text(lang.t("change_take_profit"))


@bot.message_handler(state=takeProfitStatesDoge.take_profit)
async def change_take_profit_doge(msg: types.Message, state: FSMContext):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    if msg.text.isdigit() is False:
        await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_take_profit")}</b>\nTake profit {lang.t("must_be_digit").lower()}!')
    else:
        if int(msg.text) <= 100 and int(msg.text) >= 0:
            await state.finish()
            await db.set_take_profit_doge(uid=usr['uid'], take_profit=int(msg.text))
            key = types.InlineKeyboardMarkup()
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
                callback_data='order'
            ))
            await msg.answer(f'{Emojis.ok} {lang.t("setted_take_profit")}', reply_markup=key)
        else:
            await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_take_profit")}</b>\n{lang.t("from_0_to_100").format("take profit")}!')


@bot.callback_query_handler(lambda q: q.data == 'disable_take_profit_doge')
async def dont_use_take_profit_doge(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await db.set_take_profit_doge(uid=usr['uid'], take_profit=0)
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
        callback_data='order'
    ))
    await query.answer()
    await msg.edit_text(f'{Emojis.ok} {lang.t("setted_take_profit")}', reply_markup=key)


@bot.callback_query_handler(lambda q: q.data == 'change_stop_market_doge')
async def enter_stop_market(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await stopMarketStatesDoge.stop_market.set()
    await query.answer()
    await msg.edit_text(lang.t("change_stop_market"))


@bot.message_handler(state=stopMarketStatesDoge.stop_market)
async def change_stop_market_doge(msg: types.Message, state: FSMContext):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    if msg.text.isdigit() is False:
        await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_stop_market")}</b>\nStop market {lang.t("must_be_digit").lower()}!')
    else:
        if int(msg.text) <= 100 and int(msg.text) >= 0:
            await state.finish()
            await db.set_stop_market_doge(uid=usr['uid'], stop_market=int(msg.text))
            key = types.InlineKeyboardMarkup()
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
                callback_data='order'
            ))
            await msg.answer(f'{Emojis.ok} {lang.t("setted_stop_market")}', reply_markup=key)
        else:
            await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_stop_market")}</b>\n{lang.t("from_0_to_100").format("stop market")}!')


@bot.callback_query_handler(lambda q: q.data == 'disable_stop_market_doge')
async def dont_use_stop_market_usdt(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await db.set_stop_market_doge(uid=usr['uid'], stop_market=0)
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
        callback_data='order'
    ))
    await query.answer()
    await msg.edit_text(f'{Emojis.ok} {lang.t("setted_stop_market")}', reply_markup=key)
