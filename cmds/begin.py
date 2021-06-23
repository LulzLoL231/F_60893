# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: begin.
#  Created by LulzLoL231 at 23/6/21
#
from logging import getLogger

from aiogram import types

from emojis import Emojis
from config import config
from runtime import bot, langs, db


log = getLogger(config.NAME)


@bot.callback_query_handler(lambda q: q.data == 'begin')
async def begin(query: types.CallbackQuery):
    '''Начинаем объяснять что делает бот.

    Args:
        query (types.CallbackQuery): Telegram callback query.
    '''
    msg = query.message
    log.info(f'"cmds.begin.begin": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(msg.chat.id)
    lang = langs.get_language(usr['language'])
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.usd} {lang.t("buy_premium")}',
        callback_data='fs_buy_sub'
    ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.question} F.A.Q.',
        callback_data='faq'
    ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.horn} {lang.t("offer_start")}',
        callback_data='offers'
    ))
    if usr:
        cnt = lang.t('begin')
        cnt += f'\n\n{lang.t("begin1").format(moneyface=Emojis.moneyface)}'
        cnt += f'\n\n{lang.t("begin2")}'
        cnt += f'\n\n{lang.t("begin3")}'
        await query.answer()
        await msg.edit_text(cnt)
        await msg.edit_reply_markup(key)
    else:
        await query.answer()
        log.info(f'"cmds.faq.faq": User {msg.chat.mention} ({str(msg.chat.id)}) not found in DB.')
        await msg.edit_text(lang.t('user_404'))
