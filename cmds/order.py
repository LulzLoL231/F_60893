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


class amountStates(StatesGroup):
    amount = State()


class takeProfitStates(StatesGroup):
    take_profit = State()


class stopMarketStates(StatesGroup):
    stop_market = State()


@bot.callback_query_handler(lambda q: q.data == 'order')
async def order(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await query.answer()
    await msg.edit_text(f'<code>{lang.t("fetching_order")}...</code>')
    cnt = f'''{Emojis.usd} <b>{lang.t("order_status_active") if usr["premium"] else lang.t("order_status_disabled")}</b>

<b>{lang.t("detail")}</b>
{lang.t("amount")}: <b>{usr["order_amount"]}</b>
{lang.t("take_profit")}: <b>{usr["take_profit"] if usr["take_profit"] else lang.t("not_used")}%</b>
{lang.t("stop_market")}: <b>{usr["stop_market"] if usr["stop_market"] else lang.t("not_used")}%</b>
'''
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.pen} {lang.t("change")} "{lang.t("amount")}"',
        callback_data='change_amount'
    ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.pen} {lang.t("change")} "{lang.t("take_profit")}"',
        callback_data='change_take_profit'
    ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.pen} {lang.t("change")} "{lang.t("stop_market")}"',
        callback_data='change_stop_market'
    ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("main_menu").lower()}',
        callback_data='main_menu'
    ))
    await msg.edit_text(cnt)
    await msg.edit_reply_markup(key)


@bot.callback_query_handler(lambda q: q.data == 'change_amount')
async def enter_amount(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await amountStates.amount.set()
    await query.answer()
    await msg.edit_text(lang.t("change_amount"))


@bot.message_handler(state=amountStates.amount)
async def change_amount(msg: types.Message, state: FSMContext):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    await state.finish()
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    if msg.text.isdigit() is False:
        await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_amount")}</b>')
        return None
    ev = await msg.answer(f'<code>{lang.t("changing")}...</code>')
    await db.set_order_amount(uid=usr['uid'], amount=int(msg.text))
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
        callback_data='order'
    ))
    await ev.edit_text(f'{Emojis.ok} {lang.t("setted_amount")}')
    await ev.edit_reply_markup(key)


@bot.callback_query_handler(lambda q: q.data == 'change_take_profit')
async def enter_take_profit(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await takeProfitStates.take_profit.set()
    await query.answer()
    await msg.edit_text(lang.t("change_take_profit"))


@bot.message_handler(state=takeProfitStates.take_profit)
async def change_take_profit(msg: types.Message, state: FSMContext):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    await state.finish()
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    if msg.text.isdigit() is False:
        await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_take_profit")}</b>')
        return None
    ev = await msg.answer(f'<code>{lang.t("changing")}...</code>')
    await db.set_take_profit(uid=usr['uid'], take_profit=int(msg.text))
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
        callback_data='order'
    ))
    await ev.edit_text(f'{Emojis.ok} {lang.t("setted_take_profit")}')
    await ev.edit_reply_markup(key)


@bot.callback_query_handler(lambda q: q.data == 'change_stop_market')
async def enter_stop_market(query: types.CallbackQuery):
    msg = query.message
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await stopMarketStates.stop_market.set()
    await query.answer()
    await msg.edit_text(lang.t("change_stop_market"))


@bot.message_handler(state=stopMarketStates.stop_market)
async def change_stop_market(msg: types.Message, state: FSMContext):
    await msg.answer_chat_action(types.ChatActions.TYPING)
    await state.finish()
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    if msg.text.isdigit() is False:
        await msg.answer(f'{Emojis.error} <b>{lang.t("incorrect_stop_market")}</b>')
        return None
    ev = await msg.answer(f'<code>{lang.t("changing")}...</code>')
    await db.set_stop_market(uid=usr['uid'], stop_market=int(msg.text))
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("order").lower()}',
        callback_data='order'
    ))
    await ev.edit_text(f'{Emojis.ok} {lang.t("setted_stop_market")}')
    await ev.edit_reply_markup(key)
