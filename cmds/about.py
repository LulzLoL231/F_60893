# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: about.
#  Created by LulzLoL231 at 17/6/21
#
from logging import getLogger
from typing import Dict, Union

from aiogram import types

from emojis import Emojis

from config import config
from runtime import bot, langs, db


log = getLogger(config.NAME)


async def get_about_data(id: str, secret: str) -> Dict[str, Union[str, int]]:
    '''Возвращает данные о пользователе с биржи.

    Args:
        id (str): API ID.
        secret (str): API secret.

    Returns:
        Dict[str, Union[str, int]]: Данные с биржи.
    '''
    # TODO: Make real data fetching from stocks.
    temp: Dict[str, Union[str, int]] = [
        {'accountAlias': 'XqTioCoCsRmY', 'asset': 'USDT', 'balance': '30.40592757', 'withdrawAvailable': '30.40592757', 'updateTime': 1622713242722},
        {'accountAlias': 'XqTioCoCsRmY', 'asset': 'DOGE', 'balance': '0.00000000', 'withdrawAvailable': '0.00000000', 'updateTime': 0}
    ]
    return temp


@bot.callback_query_handler(lambda q: q.data == 'about')
async def q_about(query: types.CallbackQuery):
    msg = query.message
    log.info(f'"cmds.about.q_about": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    key = types.InlineKeyboardMarkup()
    binance = (usr["id_binance"] and usr["secret_binance"])
    if binance:
        s_data = await get_about_data(usr['id_binance'], usr['secret_binance'])
        cnt = f'{Emojis.info} <b>{lang.t("about")}</b>\n\n'
        for data in s_data:
            cnt += f'<b>{lang.t("asset")}:</b> <code>{data["asset"].upper()}</code>\n'
            cnt += f'<b>{lang.t("balance")}:</b> <code>{round(float(data["balance"]), 1)} {data["asset"].upper()}</code>\n'
            cnt += f'<b>{lang.t("withdraw_available")}:</b> <code>{round(float(data["withdrawAvailable"]), 1)} {data["asset"].upper()}</code>\n\n'
        cnt = cnt.strip()
    else:
        cnt = f'{Emojis.error} <b>{lang.t("api_404")}!</b>'
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.settings} {lang.t("apis")}',
            callback_data='apis'
        ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("main_menu").lower()}',
        callback_data='main_menu'
    ))
    await query.answer()
    await msg.edit_text(cnt)
    await msg.edit_reply_markup(key)
