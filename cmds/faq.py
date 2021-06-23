# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: faq.
#  Created by LulzLoL231 at 23/6/21
#
from logging import getLogger

from aiogram import types

from emojis import Emojis
from config import config
from runtime import bot, langs, db


log = getLogger(config.NAME)


@bot.callback_query_handler(lambda q: q.data == 'faq')
async def faq(query: types.CallbackQuery):
    '''Показываем юзеру FAQ.

    Args:
        query (types.CallbackQuery): Telegram callback query.
    '''
    msg = query.message
    log.info(f'"cmds.faq.faq": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(msg.chat.id)
    lang = langs.get_language(usr['language'])
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back")}',
        callback_data='begin'
    ))
    await query.answer()
    if usr:
        await msg.edit_text(lang.t('faq'))
        await msg.edit_reply_markup(key)
    else:
        log.info(f'"cmds.faq.faq": User {msg.chat.mention} ({str(msg.chat.id)}) not found in DB.')
        await msg.edit_text(lang.t('user_404'))
