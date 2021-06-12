# -*- coding: utf-8 -*-
#
#  F_60893 - Internationalization.
#  Created by LulzLoL231 at 10/6/21
#
import os
import json
import logging
from typing import Dict

from config import config


log = logging.getLogger(config.NAME)


class Language:
    '''Класс языка.

    Args:
        language (str): Название языка.
        lang_dict (Dict[str, str]): Словарь языка.
    '''
    def __init__(self, language: str, lang_dict: Dict[str, str]) -> None:
        self.language = language
        self.lang_dict = lang_dict

    def t(self, word: str) -> str:
        if word in self.lang_dict.keys():
            return self.lang_dict[word]
        else:
            log.error(
                f'"i18n.Language": For language "{self.language}" not found word "{word}"!')
            return f'%{word}'


class Languages:
    '''Класс сбора языков.
    '''
    def __init__(self) -> None:
        self.language = config.DEFAULT_LANG
        self.dicts: Dict[str, Dict[str, str]] = {}
        for file in os.listdir('i18n'):
            if file == '__init__.py':
                continue
            if file.endswith('.json'):
                with open(os.path.join('i18n', file), 'r', encoding='utf-8') as f:
                    self.dicts.update({file.replace('.json', ''): json.loads(f.read())})

    def get_available(self) -> list:
        '''Ворзвращает список доступных языков.

        Returns:
            list: Language list.
        '''
        return list(self.dicts.keys())

    def get_language(self, language: str = '') -> Language:
        '''Возвращает класс нужного языка.

        Args:
            language (str): language name. Defaults: "".

        Returns:
            Language: language class.
        '''
        if language:
            if language in list(self.dicts.keys()):
                return Language(language, self.dicts[language])
            else:
                log.error(f'"i18n.Languages": Not found language "{language}". Using default language: "{config.DEFAULT_LANG}"')
        return Language(config.DEFAULT_LANG, self.dicts[config.DEFAULT_LANG])
