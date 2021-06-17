# -*- coding: utf-8 -*-
#
#  F_60893 - cmds: defaults.
#  Created by LulzLoL231 at 10/6/21
#
from logging import getLogger
from datetime import datetime

from aiogram import types

from emojis import Emojis
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import config
from runtime import bot, langs, db, bot_user


log = getLogger(config.NAME)


class binanceStates(StatesGroup):
    id = State()
    secret = State()


@bot.callback_query_handler(lambda q: q.data == 'settings')
async def settings(query: types.CallbackQuery):
    '''cmd "settings": Управление настройками пользователя.

    Args:
        msg (types.Message): Telegram message.
    '''
    msg = query.message
    log.info(
        f'"cmds.settings.settings": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    if usr:
        lang = langs.get_language(usr['language'])
        cnt = f'{Emojis.settings} <b>{lang.t("settings_title")}</b>\n\n'
        cnt += f'{lang.t("user")}: '
        if msg.chat.first_name:
            if msg.chat.last_name:
                cnt += f'<b>{"_".join([msg.chat.first_name, msg.chat.last_name])}#{str(msg.chat.id)}</b>\n'
            else:
                cnt += f'<b>{msg.chat.first_name}#{str(msg.chat.id)}</b>\n'
        else:
            cnt += f'<b>#{str(msg.chat.id)}</b>\n'
        cnt += f'{lang.t("premium")}: {Emojis.on if usr["premium"] else Emojis.off} <b>'
        cnt += lang.t('active') if usr['premium'] else lang.t('disabled')
        cnt += '</b>\n'
        if usr['premium']:
            cnt += f'{lang.t("premium")} {lang.t("from")}: '
            cnt += f'<b>{usr["premium_start"].ctime()}</b>\n'
            cnt += f'{lang.t("premium")} {lang.t("to")}: '
            cnt += f'<b>{usr["premium_end"].ctime()}</b>\n'
        cnt += f'{lang.t("lang")}: '
        if usr['language'] == 'ru':
            cnt += f'{Emojis.russia} <b>Русский</b>'
        elif usr['language'] == 'en':
            cnt += f'{Emojis.english} <b>English</b>'
        elif usr['language'] == 'es':
            cnt += f'{Emojis.espanol} <b>Espanol</b>'
        key = types.InlineKeyboardMarkup()
        if usr['premium'] is False:
            key.add(
                types.InlineKeyboardButton(
                    text=f'{Emojis.usd} {lang.t("pay_sub")}',
                    callback_data='fs_buy_sub'
                )
            )
        if usr['premium'] and (usr['premium_end'] - datetime.now()).total_seconds() <= config.PREMIUM_EXP_NOTIFY_SECS:
            cnt += f'\n\n<b>{lang.t("dont_forget_renew")}!</b>'
            key.add(
                types.InlineKeyboardButton(
                    text=f'{Emojis.renew} {lang.t("renew")} {lang.t("premium").lower()}.',
                    callback_data='renew_premium'
                )
            )
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.pen} {lang.t("change")} {lang.t("apis")}',
            callback_data="apis"
        ))
        key.add(
            types.InlineKeyboardButton(
                text=f'{Emojis.pen} {lang.t("change")} {lang.t("lang").lower()}',
                callback_data='change_lang'
            )
        )
        key.add(
            types.InlineKeyboardButton(
                text=f'{Emojis.no} {lang.t("delete_user")}',
                callback_data='delete_user'
            )
        )
        key.add(
            types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("main_menu").lower()}',
                callback_data='main_menu'
            )
        )
        await query.answer()
        if msg.from_user != bot_user:
            await msg.answer(cnt, reply_markup=key)
        else:
            await msg.edit_text(cnt)
            await msg.edit_reply_markup(key)
    else:
        await query.answer()
        await msg.edit_text(f'<code>{langs.get_language(config.DEFAULT_LANG).t("user_404")}</code>')


@bot.callback_query_handler(lambda q: q.data == 'change_lang')
async def change_lang(query: types.CallbackQuery):
    '''cmd "change_lang": Изменение языка.

    Args:
        msg (types.CallbackQuery): Telegram message query.
    '''
    msg = query.message
    log.info(
        f'"cmds.settings.change_lang": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    if usr:
        lang = langs.get_language(usr['language'])
        cnt = f'<b>{lang.t("choice_lang")}</b>'
        key = types.InlineKeyboardMarkup()
        if usr['language'] == 'ru':
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.english} English',
                callback_data='chg_lang_to_en'
            ))
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.espanol} Espanol',
                callback_data='chg_lang_to_es'
            ))
        elif usr['language'] == 'en':
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.russia} Русский',
                callback_data='chg_lang_to_ru'
            ))
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.espanol} Espanol',
                callback_data='chg_lang_to_es'
            ))
        elif usr['language'] == 'es':
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.english} English',
                callback_data='chg_lang_to_en'
            ))
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.russia} Русский',
                callback_data='chg_lang_to_ru'
            ))
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
            callback_data='settings'
        ))
        await query.answer()
        await msg.edit_text(cnt)
        await msg.edit_reply_markup(key)
    else:
        await query.answer()
        await msg.edit_text(f'<code>{langs.get_language(config.DEFAULT_LANG).t("user_404")}</code>')


@bot.callback_query_handler(lambda q: q.data == 'chg_lang_to_en')
async def chg_lang_to_en(query: types.CallbackQuery):
    '''cmd "chg_lang_to_en": Изменение языка на английский.

    Args:
        msg (types.CallbackQuery): Telegram message query.
    '''
    msg = query.message
    log.info(
        f'"cmds.settings.chg_lang_to_en": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    if usr:
        lang = langs.get_language(usr['language'])
        await query.answer()
        await msg.answer_chat_action(types.ChatActions.TYPING)
        res = await db.set_user_lang(uid=msg.chat.id, lang='en')
        key = types.InlineKeyboardMarkup()
        if res:
            usr = await db.get_user(uid=msg.chat.id)
            lang = langs.get_language(usr['language'])
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
                callback_data='settings'
            ))
            await msg.edit_text(f'<b>{lang.t("lang")} {lang.t("changed").lower()}!</b>')
            await msg.edit_reply_markup(key)
        else:
            await msg.edit_text(f'{Emojis.error} <code>{lang.t("change_error")} {lang.t("lang")}</code>')
            await msg.edit_reply_markup(key)
    else:
        await query.answer()
        await msg.edit_text(f'<code>{langs.get_language(config.DEFAULT_LANG).t("user_404")}</code>')


@bot.callback_query_handler(lambda q: q.data == 'chg_lang_to_ru')
async def chg_lang_to_ru(query: types.CallbackQuery):
    '''cmd "chg_lang_to_ru": Изменение языка на русский.

    Args:
        msg (types.CallbackQuery): Telegram message query.
    '''
    msg = query.message
    log.info(
        f'"cmds.settings.chg_lang_to_ru": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    if usr:
        lang = langs.get_language(usr['language'])
        await query.answer()
        await msg.answer_chat_action(types.ChatActions.TYPING)
        res = await db.set_user_lang(uid=msg.chat.id, lang='ru')
        key = types.InlineKeyboardMarkup()
        if res:
            usr = await db.get_user(uid=msg.chat.id)
            lang = langs.get_language(usr['language'])
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
                callback_data='settings'
            ))
            await msg.edit_text(f'<b>{lang.t("lang")} {lang.t("changed").lower()}!</b>')
            await msg.edit_reply_markup(key)
        else:
            await msg.edit_text(f'{Emojis.error} <code>{lang.t("change_error")} {lang.t("lang").lower()}</code>')
            await msg.edit_reply_markup(key)
    else:
        await query.answer()
        await msg.edit_text(f'<code>{langs.get_language(config.DEFAULT_LANG).t("user_404")}</code>')


@bot.callback_query_handler(lambda q: q.data == 'chg_lang_to_es')
async def chg_lang_to_es(query: types.CallbackQuery):
    '''cmd "chg_lang_to_es": Изменение языка на испанский.

    Args:
        msg (types.CallbackQuery): Telegram message query.
    '''
    msg = query.message
    log.info(
        f'"cmds.settings.chg_lang_to_es": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    if usr:
        lang = langs.get_language(usr['language'])
        await query.answer()
        await msg.answer_chat_action(types.ChatActions.TYPING)
        res = await db.set_user_lang(uid=msg.chat.id, lang='es')
        key = types.InlineKeyboardMarkup()
        if res:
            usr = await db.get_user(uid=msg.chat.id)
            lang = langs.get_language(usr['language'])
            key.add(types.InlineKeyboardButton(
                text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
                callback_data='settings'
            ))
            await msg.edit_text(f'<b>{lang.t("lang")} {lang.t("changed").lower()}!</b>')
            await msg.edit_reply_markup(key)
        else:
            await msg.edit_text(f'{Emojis.error} <code>{lang.t("change_error")} {lang.t("lang").lower()}</code>')
            await msg.edit_reply_markup(key)
    else:
        await query.answer()
        await msg.edit_text(f'<code>{langs.get_language(config.DEFAULT_LANG).t("user_404")}</code>')


@bot.callback_query_handler(lambda q: q.data == 'delete_user')
async def delete_user(query: types.CallbackQuery):
    '''cmd "delete_user": Запрос на удаление пользователя.

    Args:
        msg (types.CallbackQuery): Telegram message query.
    '''
    msg = query.message
    log.info(
        f'"cmds.settings.delete_user": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    key = types.InlineKeyboardMarkup()
    if usr:
        lang = langs.get_language(usr['language'])
        key.add(types.InlineKeyboardButton(
            text=lang.t('confirm'),
            callback_data='confirmed_delete_user'
        ))
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
            callback_data='settings'
        ))
        await query.answer()
        await msg.edit_text(lang.t('user_del_warn'))
        await msg.edit_reply_markup(key)
    else:
        lang = langs.get_language(config.DEFAULT_LANG)
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
            callback_data='settings'
        ))
        await query.answer()
        await msg.edit_text(f'{Emojis.error} <code>{lang.t("change_error")} {lang.t("lang").lower()}</code>')
        await msg.edit_reply_markup(key)


@bot.callback_query_handler(lambda q: q.data == 'confirmed_delete_user')
async def confirmed_delete_user(query: types.CallbackQuery):
    '''cmd "confirmed_delete_user": Удаляет пользователя из БД.

    Args:
        msg (types.CallbackQuery): Telegram message query.
    '''
    msg = query.message
    log.info(
        f'"cmds.settings.confirmed_delete_user": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    key = types.InlineKeyboardMarkup()
    await query.answer()
    if usr:
        lang = langs.get_language(usr['language'])
        await msg.edit_text(f'<code>{lang.t("deleting")}...</code>')
        await msg.answer_chat_action(types.ChatActions.TYPING)
        res = await db.del_user(uid=usr['uid'])
        if res:
            log.info(f'"cmds.settings.confirmed_delete_user": User #{str(msg.chat.id)} has been deleted from DB!')
            await msg.edit_text(f'{Emojis.ok} <b>{lang.t("delete_ok")}</b>')
        else:
            await msg.edit_text(f'{Emojis.error} <b>{lang.t("delete_err")}</b>')
    else:
        lang = langs.get_language(config.DEFAULT_LANG)
        key.add(types.InlineKeyboardButton(
            text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
            callback_data='settings'
        ))
        await msg.edit_text(f'{Emojis.error} <code>{lang.t("change_error")} {lang.t("lang").lower()}</code>')
        await msg.edit_reply_markup(key)


@bot.callback_query_handler(lambda q: q.data == 'apis')
async def apis(query: types.CallbackQuery):
    '''cmd "apis": Управление API бирж.

    Args:
        msg (types.CallbackQuery): Telegram message query.
    '''
    msg = query.message
    log.info(
        f'"cmds.settings.apis": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    key = types.InlineKeyboardMarkup()
    lang = langs.get_language(usr['language'])
    binance = (usr["id_binance"] and usr["secret_binance"])
    cnt = f'''{Emojis.settings} {lang.t("settings")} {lang.t("apis")}

<b>{lang.t("stock")}: Binance</b>
{lang.t("status")}: {Emojis.ok if binance else Emojis.no} {lang.t("setted") if binance else lang.t("not_setted")}
'''
    if binance:
        cnt += f'API ID: <code>{usr["id_binance"]}</code>'
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.pen} {lang.t("change_binance")}',
        callback_data='change_binance'
    ))
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("settings").lower()}',
        callback_data='settings'
    ))
    await query.answer()
    await msg.edit_text(cnt)
    await msg.edit_reply_markup(key)


@bot.callback_query_handler(lambda q: q.data == 'apis_state', state='*')
async def apis_state(query: types.CallbackQuery):
    state = bot.current_state(chat=query.message.chat.id)
    await state.finish()
    await apis(query)


@bot.callback_query_handler(lambda q: q.data == 'change_binance')
async def change_binance_id(query: types.CallbackQuery):
    msg = query.message
    log.info(
        f'"cmds.settings.change_binance_id": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr["language"])
    await binanceStates.id.set()
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("apis").lower()}',
        callback_data='apis_state'
    ))
    await query.answer()
    await msg.edit_text(f'{lang.t("change_binance_id")}')
    await msg.edit_reply_markup(key)


@bot.message_handler(state=binanceStates.id)
async def change_binance_secret(msg: types.Message, state: FSMContext):
    log.info(
        f'"cmds.settings.change_binance_secret": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await msg.answer_chat_action(types.ChatActions.TYPING)
    await state.update_data({'id': msg.text, 'uid': msg.chat.id})
    usr = await db.get_user(uid=msg.chat.id)
    lang = langs.get_language(usr['language'])
    await binanceStates.secret.set()
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("apis").lower()}',
        callback_data='apis_state'
    ))
    await msg.answer(lang.t('change_binance_secret'), reply_markup=key)


@bot.message_handler(state=binanceStates.secret)
async def change_binance_data(msg: types.Message, state: FSMContext):
    log.info(
        f'"cmds.settings.change_binance_data": Called by {msg.chat.mention} ({str(msg.chat.id)})')
    await msg.answer_chat_action(types.ChatActions.TYPING)
    data = await state.get_data()
    await state.finish()
    usr = await db.get_user(uid=data['uid'])
    lang = langs.get_language(usr['language'])
    ev = await msg.answer(f'<code>{lang.t("changing")}...</code>')
    await db.set_binance(uid=data['uid'], id=data['id'], secret=msg.text)
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton(
        text=f'{Emojis.back} {lang.t("back_to")} {lang.t("apis").lower()}',
        callback_data='apis'
    ))
    await ev.edit_text(f'{Emojis.ok} {lang.t("setted_binance")}!')
    await ev.edit_reply_markup(key)
